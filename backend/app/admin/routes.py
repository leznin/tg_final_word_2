"""
Admin panel routes
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.services.users import UserService
from app.core.config import settings

admin_router = APIRouter()


@admin_router.get("/", response_class=HTMLResponse)
async def admin_dashboard():
    from fastapi.responses import Response
    admin_key = settings.ADMIN_SECRET_KEY
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Admin Panel</title>
        <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
        <meta http-equiv="Pragma" content="no-cache">
        <meta http-equiv="Expires" content="0">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .stats {{ display: flex; gap: 20px; margin: 20px 0; }}
            .stat-card {{ border: 1px solid #ddd; padding: 20px; border-radius: 5px; }}
            nav {{ margin-bottom: 20px; }}
            nav a {{ margin-right: 15px; text-decoration: none; padding: 10px; background: #f0f0f0; border-radius: 3px; }}
        </style>
    </head>
    <body>
        <h1>Admin Panel</h1>
        <nav>
            <a href="/admin/">Dashboard</a>
            <a href="/admin/chats">Chats</a>
            <a href="/admin/users">Users</a>
            <a href="/admin/broadcast">Broadcast</a>
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
            fetch('/api/v1/users', {{ headers: {{ 'X-Admin-Key': '{admin_key}' }} }})
                .then(r => r.json())
                .then(data => document.getElementById('user-count').textContent = data.length)
                .catch(error => {{
                    console.error('Error loading users:', error);
                    document.getElementById('user-count').textContent = 'Error loading';
                }});

            fetch('/api/v1/messages/count', {{ headers: {{ 'X-Admin-Key': '{admin_key}' }} }})
                .then(r => r.json())
                .then(data => document.getElementById('message-count').textContent = data.total_messages)
                .catch(error => {{
                    console.error('Error loading messages:', error);
                    document.getElementById('message-count').textContent = 'Error loading';
                }});
        </script>
    </body>
    </html>
    """

    response = Response(content=html_content, media_type="text/html")
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


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
            <a href="/admin/broadcast">Broadcast</a>
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
async def admin_chats():
    """Admin chats page"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Admin - Chats</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            nav { margin-bottom: 20px; }
            nav a { margin-right: 15px; text-decoration: none; padding: 10px; background: #f0f0f0; border-radius: 3px; }
        </style>
    </head>
    <body>
        <h1>Chats Management</h1>
        <nav>
            <a href="/admin/">Dashboard</a>
            <a href="/admin/chats">Chats</a>
            <a href="/admin/users">Users</a>
            <a href="/admin/broadcast">Broadcast</a>
            <a href="/admin/settings">Settings</a>
        </nav>
        <p>Chat management functionality coming soon...</p>
    </body>
    </html>
    """


@admin_router.get("/settings", response_class=HTMLResponse)
async def admin_settings():
    """Admin settings page"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Admin - Settings</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            nav { margin-bottom: 20px; }
            nav a { margin-right: 15px; text-decoration: none; padding: 10px; background: #f0f0f0; border-radius: 3px; }
        </style>
    </head>
    <body>
        <h1>Settings</h1>
        <nav>
            <a href="/admin/">Dashboard</a>
            <a href="/admin/chats">Chats</a>
            <a href="/admin/users">Users</a>
            <a href="/admin/broadcast">Broadcast</a>
            <a href="/admin/settings">Settings</a>
        </nav>
        <p>Settings functionality coming soon...</p>
    </body>
    </html>
    """


@admin_router.get("/broadcast", response_class=HTMLResponse)
async def admin_broadcast():
    """Admin broadcast page"""
    admin_key = settings.ADMIN_SECRET_KEY
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Admin - Broadcast</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            nav {{ margin-bottom: 20px; }}
            nav a {{ margin-right: 15px; text-decoration: none; padding: 10px; background: #f0f0f0; border-radius: 3px; }}
            .broadcast-form {{ max-width: 600px; margin: 20px 0; }}
            .form-group {{ margin-bottom: 15px; }}
            label {{ display: block; margin-bottom: 5px; font-weight: bold; }}
            textarea {{ width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; resize: vertical; min-height: 150px; }}
            input[type="text"], input[type="url"] {{ width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }}
            select {{ width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }}
            button {{ padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }}
            button:hover {{ background: #0056b3; }}
            button:disabled {{ background: #6c757d; cursor: not-allowed; }}
            .media-section {{ border: 1px solid #ddd; border-radius: 4px; padding: 15px; margin: 15px 0; }}
            .keyboard-section {{ border: 1px solid #ddd; border-radius: 4px; padding: 15px; margin: 15px 0; }}
            .button-row {{ display: flex; gap: 10px; margin-bottom: 10px; }}
            .button-row input {{ flex: 1; }}
            .add-button {{ background: #28a745; color: white; border: none; padding: 5px 10px; border-radius: 3px; cursor: pointer; }}
            .remove-button {{ background: #dc3545; color: white; border: none; padding: 5px 10px; border-radius: 3px; cursor: pointer; }}
            .status {{ margin-top: 20px; padding: 15px; border-radius: 4px; }}
            .status.loading {{ background: #fff3cd; border: 1px solid #ffeaa7; }}
            .status.success {{ background: #d4edda; border: 1px solid #c3e6cb; }}
            .status.error {{ background: #f8d7da; border: 1px solid #f5c6cb; }}
            .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-top: 15px; }}
            .stat-item {{ background: #f8f9fa; padding: 10px; border-radius: 4px; }}
            .stat-item strong {{ display: block; font-size: 1.2em; }}
            .progress-bar {{ width: 100%; height: 20px; background: #e9ecef; border-radius: 10px; overflow: hidden; margin: 10px 0; }}
            .progress-fill {{ height: 100%; background: #007bff; transition: width 0.3s ease; }}
        </style>
    </head>
    <body>
        <h1>Broadcast Messages</h1>
        <nav>
            <a href="/admin/">Dashboard</a>
            <a href="/admin/chats">Chats</a>
            <a href="/admin/users">Users</a>
            <a href="/admin/broadcast">Broadcast</a>
            <a href="/admin/settings">Settings</a>
        </nav>

        <div class="broadcast-form">
            <div class="form-group">
                <label for="message">Message to broadcast:</label>
                <textarea id="message" placeholder="Enter your message here..."></textarea>
                <small style="color: #666;">Maximum 4096 characters. HTML formatting supported.</small>
            </div>

            <div class="media-section">
                <h3>Media (optional)</h3>
                <div class="form-group">
                    <label for="mediaType">Media Type:</label>
                    <select id="mediaType">
                        <option value="">No media</option>
                        <option value="photo">Photo</option>
                        <option value="video">Video</option>
                        <option value="document">Document</option>
                    </select>
                </div>
                <div class="form-group" id="mediaUrlGroup" style="display: none;">
                    <label for="mediaUrl">Media URL:</label>
                    <input type="url" id="mediaUrl" placeholder="https://example.com/file.jpg">
                    <small style="color: #666;">URL must be publicly accessible</small>
                </div>
                <div class="form-group" id="mediaCaptionGroup" style="display: none;">
                    <label for="mediaCaption">Media Caption:</label>
                    <input type="text" id="mediaCaption" placeholder="Caption for media file">
                </div>
            </div>

            <div class="keyboard-section">
                <h3>Inline Keyboard (optional)</h3>
                <div id="keyboardRows"></div>
                <button type="button" onclick="addKeyboardRow()">Add Button Row</button>
            </div>

            <button id="sendBtn" onclick="sendBroadcast()">Send Broadcast</button>
        </div>

        <div id="status" class="status" style="display: none;"></div>

        <div id="stats" style="display: none;">
            <h3>Broadcast Results</h3>
            <div class="stats" id="statsGrid"></div>
        </div>

        <script>
            let statusCheckInterval;

            let rowCounter = 0;

            function toggleMediaFields() {{
                const mediaType = document.getElementById('mediaType').value;
                const mediaUrlGroup = document.getElementById('mediaUrlGroup');
                const mediaCaptionGroup = document.getElementById('mediaCaptionGroup');

                if (mediaType) {{
                    mediaUrlGroup.style.display = 'block';
                    mediaCaptionGroup.style.display = 'block';
                }} else {{
                    mediaUrlGroup.style.display = 'none';
                    mediaCaptionGroup.style.display = 'none';
                }}
            }}

            function addKeyboardRow() {{
                rowCounter++;
                const keyboardRows = document.getElementById('keyboardRows');
                const rowDiv = document.createElement('div');
                rowDiv.className = 'button-row';
                rowDiv.id = `row-${{rowCounter}}`;
                rowDiv.innerHTML = `
                    <input type="text" placeholder="Button text" class="button-text">
                    <input type="url" placeholder="Button URL (optional)" class="button-url">
                    <input type="text" placeholder="Callback data (optional)" class="button-callback">
                    <button type="button" class="remove-button" onclick="removeRow(${{rowCounter}})">Remove</button>
                `;
                keyboardRows.appendChild(rowDiv);
            }}

            function removeRow(rowId) {{
                const row = document.getElementById(`row-${{rowId}}`);
                if (row) {{
                    row.remove();
                }}
            }}

            async function sendBroadcast() {{
                const message = document.getElementById('message').value.trim();
                const sendBtn = document.getElementById('sendBtn');
                const statusDiv = document.getElementById('status');

                if (!message) {{
                    showStatus('Please enter a message', 'error');
                    return;
                }}

                if (message.length > 4096) {{
                    showStatus('Message is too long (max 4096 characters)', 'error');
                    return;
                }}

                // Prepare request data
                const requestData = {{ message }};

                // Add media if provided
                const mediaType = document.getElementById('mediaType').value;
                if (mediaType) {{
                    const mediaUrl = document.getElementById('mediaUrl').value.trim();
                    const mediaCaption = document.getElementById('mediaCaption').value.trim();

                    if (!mediaUrl) {{
                        showStatus('Please enter media URL', 'error');
                        return;
                    }}

                    requestData.media = {{
                        type: mediaType,
                        url: mediaUrl,
                        caption: mediaCaption || null
                    }};
                }}

                // Add keyboard if provided
                const keyboardRows = document.querySelectorAll('.button-row');
                if (keyboardRows.length > 0) {{
                    const inlineKeyboard = [];

                    keyboardRows.forEach(row => {{
                        const text = row.querySelector('.button-text').value.trim();
                        const url = row.querySelector('.button-url').value.trim();
                        const callback = row.querySelector('.button-callback').value.trim();

                        if (text) {{
                            const button = {{ text }};
                            if (url) button.url = url;
                            if (callback) button.callback_data = callback;

                            if (!inlineKeyboard.length || inlineKeyboard[inlineKeyboard.length - 1].length >= 3) {{
                                inlineKeyboard.push([]);
                            }}
                            inlineKeyboard[inlineKeyboard.length - 1].push(button);
                        }}
                    }});

                    if (inlineKeyboard.length > 0) {{
                        requestData.reply_markup = {{ inline_keyboard: inlineKeyboard }};
                    }}
                }}

                sendBtn.disabled = true;
                sendBtn.textContent = 'Sending...';

                try {{
                    const response = await fetch('/api/v1/broadcast/send', {{
                        method: 'POST',
                        headers: {{
                            'Content-Type': 'application/json',
                            'X-Admin-Key': '{admin_key}'
                        }},
                        body: JSON.stringify(requestData)
                    }});

                    const result = await response.json();

                    if (response.ok) {{
                        showStatus('Broadcast started successfully!', 'success');
                        document.getElementById('stats').style.display = 'block';
                        displayStats(result);
                        startStatusChecking();
                    }} else {{
                        showStatus(result.detail || 'Failed to send broadcast', 'error');
                    }}
                }} catch (error) {{
                    showStatus('Network error: ' + error.message, 'error');
                }} finally {{
                    sendBtn.disabled = false;
                    sendBtn.textContent = 'Send Broadcast';
                }}
            }}

            // Initialize media fields toggle
            document.getElementById('mediaType').addEventListener('change', toggleMediaFields);

            function showStatus(message, type) {{
                const statusDiv = document.getElementById('status');
                statusDiv.textContent = message;
                statusDiv.className = `status ${{type}}`;
                statusDiv.style.display = 'block';
            }}

            function displayStats(result) {{
                const statsGrid = document.getElementById('statsGrid');
                statsGrid.innerHTML = `
                    <div class="stat-item">
                        <strong>${{result.total_users}}</strong>
                        <span>Total Users</span>
                    </div>
                    <div class="stat-item">
                        <strong>${{result.sent_successfully}}</strong>
                        <span>Sent Successfully</span>
                    </div>
                    <div class="stat-item">
                        <strong>${{result.blocked_users}}</strong>
                        <span>Blocked Users</span>
                    </div>
                    <div class="stat-item">
                        <strong>${{result.failed_sends}}</strong>
                        <span>Failed Sends</span>
                    </div>
                    <div class="stat-item">
                        <strong>${{result.duration_seconds.toFixed(1)}}s</strong>
                        <span>Duration</span>
                    </div>
                `;
            }}

            function startStatusChecking() {{
                if (statusCheckInterval) clearInterval(statusCheckInterval);
                statusCheckInterval = setInterval(async () => {{
                    try {{
                        const response = await fetch('/api/v1/broadcast/status', {{
                            headers: {{ 'X-Admin-Key': '{admin_key}' }}
                        }});
                        const status = await response.json();

                        if (!status.is_running) {{
                            clearInterval(statusCheckInterval);
                            showStatus('Broadcast completed!', 'success');
                        }}
                    }} catch (error) {{
                        console.error('Status check failed:', error);
                    }}
                }}, 2000);
            }}

            // Load initial user count
            fetch('/api/v1/broadcast/users/count', {{
                headers: {{ 'X-Admin-Key': '{admin_key}' }}
            }})
            .then(r => r.json())
            .then(data => {{
                document.getElementById('message').placeholder = `Enter your message here... (${{data.count}} users will receive it)`;
            }})
            .catch(error => console.error('Failed to load user count:', error));
        </script>
    </body>
    </html>
    """


