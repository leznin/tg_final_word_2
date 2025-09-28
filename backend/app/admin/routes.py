"""
Admin panel routes
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.services.users import UserService

admin_router = APIRouter()


@admin_router.get("/", response_class=HTMLResponse)
async def admin_dashboard():
    """Admin dashboard"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Admin Panel</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .stats { display: flex; gap: 20px; margin: 20px 0; }
            .stat-card { border: 1px solid #ddd; padding: 20px; border-radius: 5px; }
            nav { margin-bottom: 20px; }
            nav a { margin-right: 15px; text-decoration: none; padding: 10px; background: #f0f0f0; border-radius: 3px; }
        </style>
    </head>
    <body>
        <h1>Admin Panel</h1>
        <nav>
            <a href="/admin/">Dashboard</a>
            <a href="/admin/chats">Chats</a>
            <a href="/admin/users">Users</a>
            <a href="/admin/settings">Settings</a>
        </nav>

        <div class="stats">
            <div class="stat-card">
                <h3>Users</h3>
                <p id="user-count">Loading...</p>
            </div>
            <div class="stat-card">
                <h3>Messages</h3>
                <p id="message-count">Loading...</p>
            </div>
        </div>

        <script>
            // Load statistics
            fetch('/api/v1/users', { headers: { 'X-Admin-Key': 'admin-secret-key' } })
                .then(r => r.json())
                .then(data => document.getElementById('user-count').textContent = data.length);

            fetch('/api/v1/telegram/messages', { headers: { 'X-Admin-Key': 'admin-secret-key' } })
                .then(r => r.json())
                .then(data => document.getElementById('message-count').textContent = data.length);
        </script>
    </body>
    </html>
    """


@admin_router.get("/users", response_class=HTMLResponse)
async def admin_users(db: AsyncSession = Depends(get_db)):
    """Admin users page"""
    user_service = UserService(db)
    users = await user_service.get_users()

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Admin - Users</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            nav {{ margin-bottom: 20px; }}
            nav a {{ margin-right: 15px; text-decoration: none; padding: 10px; background: #f0f0f0; border-radius: 3px; }}
        </style>
    </head>
    <body>
        <h1>Users Management</h1>
        <nav>
            <a href="/admin/">Dashboard</a>
            <a href="/admin/chats">Chats</a>
            <a href="/admin/users">Users</a>
            <a href="/admin/settings">Settings</a>
        </nav>

        <table>
            <tr>
                <th>ID</th>
                <th>Username</th>
                <th>Email</th>
                <th>Telegram ID</th>
                <th>Is Admin</th>
                <th>Created</th>
            </tr>
    """

    for user in users:
        html += f"""
            <tr>
                <td>{user.id}</td>
                <td>{user.username or '-'}</td>
                <td>{user.email or '-'}</td>
                <td>{user.telegram_id or '-'}</td>
                <td>{'Yes' if user.is_admin else 'No'}</td>
                <td>{user.created_at}</td>
            </tr>
        """

    html += """
        </table>
    </body>
    </html>
    """

    return html


@admin_router.get("/chats", response_class=HTMLResponse)
async def admin_chats(db: AsyncSession = Depends(get_db)):
    """Admin chats page"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Admin - Chats</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            table { border-collapse: collapse; width: 100%; margin-top: 20px; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; font-size: 14px; }
            th { background-color: #f2f2f2; position: sticky; top: 0; }
            .stats { display: flex; gap: 20px; margin: 20px 0; flex-wrap: wrap; }
            .stat-card { border: 1px solid #ddd; padding: 15px; border-radius: 5px; min-width: 150px; }
            .stat-number { font-size: 24px; font-weight: bold; color: #333; }
            .stat-label { font-size: 14px; color: #666; margin-top: 5px; }
            nav { margin-bottom: 20px; }
            nav a { margin-right: 15px; text-decoration: none; padding: 10px; background: #f0f0f0; border-radius: 3px; }
            nav a:hover { background: #e0e0e0; }
            .loading { text-align: center; padding: 20px; }
            .chat-type { padding: 2px 6px; border-radius: 3px; font-size: 12px; font-weight: bold; }
            .type-group { background: #e3f2fd; color: #1976d2; }
            .type-supergroup { background: #f3e5f5; color: #7b1fa2; }
            .type-channel { background: #fff3e0; color: #f57c00; }
            .moderators-count { text-align: center; }
            .linked-channel { font-style: italic; color: #666; }
            .no-data { text-align: center; padding: 40px; color: #666; }
        </style>
    </head>
    <body>
        <h1>Chats Management</h1>
        <nav>
            <a href="/admin/">Dashboard</a>
            <a href="/admin/chats">Chats</a>
            <a href="/admin/users">Users</a>
            <a href="/admin/settings">Settings</a>
        </nav>

        <div class="stats" id="stats">
            <div class="stat-card">
                <div class="stat-number" id="total-chats">Loading...</div>
                <div class="stat-label">Total Chats</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="groups">Loading...</div>
                <div class="stat-label">Groups</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="supergroups">Loading...</div>
                <div class="stat-label">Supergroups</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="channels">Loading...</div>
                <div class="stat-label">Channels</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="with-channels">Loading...</div>
                <div class="stat-label">With Linked Channels</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="with-moderators">Loading...</div>
                <div class="stat-label">With Moderators</div>
            </div>
        </div>

        <div id="content">
            <div class="loading">Loading chats data...</div>
        </div>

        <script>
            async function loadStats() {
                try {
                    const response = await fetch('/api/v1/admin-chats/stats', {
                        headers: { 'X-Admin-Key': 'admin-secret-key' }
                    });
                    const stats = await response.json();

                    document.getElementById('total-chats').textContent = stats.total_chats;
                    document.getElementById('groups').textContent = stats.groups;
                    document.getElementById('supergroups').textContent = stats.supergroups;
                    document.getElementById('channels').textContent = stats.channels;
                    document.getElementById('with-channels').textContent = stats.chats_with_linked_channels;
                    document.getElementById('with-moderators').textContent = stats.chats_with_moderators;
                } catch (error) {
                    console.error('Error loading stats:', error);
                }
            }

            async function loadChats() {
                try {
                    const response = await fetch('/api/v1/admin-chats/', {
                        headers: { 'X-Admin-Key': 'admin-secret-key' }
                    });
                    const chats = await response.json();

                    if (chats.length === 0) {
                        document.getElementById('content').innerHTML = '<div class="no-data">No chats found</div>';
                        return;
                    }

                    let html = `
                        <table>
                            <tr>
                                <th>ID</th>
                                <th>Telegram ID</th>
                                <th>Title</th>
                                <th>Type</th>
                                <th>Username</th>
                                <th>Added By</th>
                                <th>Added At</th>
                                <th>Moderators</th>
                                <th>Linked Channel</th>
                                <th>Edit Timeout</th>
                            </tr>
                    `;

                    chats.forEach(chat => {
                        const typeClass = `type-${chat.chat_type}`;
                        const linkedChannel = chat.linked_channel ?
                            `${chat.linked_channel.title || 'N/A'} (${chat.linked_channel.username || 'N/A'})` :
                            '-';
                        const editTimeout = chat.message_edit_timeout_minutes ?
                            `${chat.message_edit_timeout_minutes} min` : '-';

                        html += `
                            <tr>
                                <td>${chat.id}</td>
                                <td><code>${chat.telegram_chat_id}</code></td>
                                <td>${chat.title || '-'}</td>
                                <td><span class="chat-type ${typeClass}">${chat.chat_type}</span></td>
                                <td>${chat.username ? '@' + chat.username : '-'}</td>
                                <td>${chat.added_by_user.username || chat.added_by_user.email || 'ID: ' + chat.added_by_user.id}</td>
                                <td>${new Date(chat.added_at).toLocaleString()}</td>
                                <td class="moderators-count">${chat.moderator_count}</td>
                                <td class="linked-channel">${linkedChannel}</td>
                                <td>${editTimeout}</td>
                            </tr>
                        `;
                    });

                    html += '</table>';
                    document.getElementById('content').innerHTML = html;
                } catch (error) {
                    console.error('Error loading chats:', error);
                    document.getElementById('content').innerHTML = '<div class="no-data">Error loading chats data</div>';
                }
            }

            // Load data when page loads
            loadStats();
            loadChats();
        </script>
    </body>
    </html>
    """

    return html


