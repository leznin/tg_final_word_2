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


