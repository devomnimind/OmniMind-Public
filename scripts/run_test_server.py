"""
OmniMind Project - Artificial Consciousness System
Copyright (C) 2024-2025 Fabrício da Silva

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

Contact: fabricioslv@hotmail.com.br
"""

import sys
import os
import uvicorn

# Add current directory to sys.path
sys.path.append(os.getcwd())

if __name__ == "__main__":
    try:
        # Import the app
        from web.backend.main import app

        uvicorn.run(app, host="127.0.0.1", port=8001)
    except Exception as e:
        print(f"Failed to start server: {e}")
        sys.exit(1)
