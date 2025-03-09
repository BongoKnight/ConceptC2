from flask import Flask, request
from pathlib import Path
from textual import on, work
from textual.reactive import var
from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Button, Label, Collapsible, Select, Input
import webbrowser
import requests
from datetime import datetime, timedelta



URL = "http://www.strava.com/oauth/authorize?client_id=148429&response_type=code&redirect_uri=http://localhost:5000/exchange_token&approval_prompt=force&scope=read,profile:read_all,profile:write,activity:read,activity:write"
MAIN_ACTIVITY = ""
CODE = ""

def post_activity(description: str, machine:str, token=""):
    headers = {
        'Authorization': f"Bearer {token}",
        'Content-Type': 'application/json',
    }
    json_data = {
        'commute': 0,
        'description': description,
        'distance': '3400',
        'elapsed_time': '1200',
        'name': f"{machine}-Small run",
        'sport_type': 'Run',
        'start_date_local': (datetime.now() - timedelta(minutes=20)).isoformat() ,
        'trainer': 0,
        'type': 'Run',
    }

    response = requests.post('https://www.strava.com/api/v3/activities', headers=headers, json=json_data)
    return response

def update_activity_description(activity_id:int = MAIN_ACTIVITY, description:str = "", token = "") -> requests.Response:
    headers = {
        'Authorization': f"Bearer {token}",
        'Content-Type': 'application/json',
    }
    json_data = {
        "description":description
    }
    response = requests.put(f"https://www.strava.com/api/v3/activities/{activity_id}", headers=headers, json=json_data)
    return response



app = Flask(__name__)
@app.route('/exchange_token')
def hello_world():
    with open(Path(__file__).parent/"code", "w+") as f:
        f.write(request.args.get('code'))
    return 'Code Token saved!'

class ConceptC2Server(App):
    """A Textual app to manage Concept C2."""
    DEFAULT_CSS = """
    #refresh-label{
        width: auto;
    }
    """

    access_token = var("")

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        with Collapsible(title="Refresh OAuth token",collapsed=False):
            yield Label("You should refresh the OAuth API, for that click the button bellow and confirm access to your Strava account. Once validated, you can close the running Flask server with Ctrl+C", id="refresh-label")
            yield Button("Refresh!", variant="success", id="refresh")
        yield Select(options=[], prompt="Machine")
        yield Input(placeholder="Enter command to send")
        yield Footer()

    @on(Input.Submitted)
    def post_command(self, event: Input.Submitted):
        client_machine = self.query_one(Select).value
        command = event.input.value
        response = post_activity(command, client_machine, self.access_token)
        if response.status_code == 200:
            self.notify("New command to execute added!")
        else:
            self.notify(f"Error : {str(response.json())}")

    @on(Button.Pressed, "#refresh")
    def recover_token(self):
        webbrowser.open_new_tab(URL)
        with self.suspend():
            app.run()
        with open(Path(__file__).parent / "code","r") as f:
            CODE = f.read()
            files = {
                'client_id': (None, '<client_id>'),
                'client_secret': (None, '<client_secret>'),
                'code': (None, CODE),
                'grant_type': (None, 'authorization_code'),
            }
            response = requests.post('https://www.strava.com/oauth/token', files=files)
            if response.status_code == 200:
                self.access_token = response.json().get("access_token")
            update_response = update_activity_description(MAIN_ACTIVITY, self.access_token, self.access_token)
            if update_response.status_code == 200:
                self.notify("OAuth Token refreshed")
            else:
                self.notify(f"Error while setting OAuth Token: {CODE, self.access_token, update_response.json()}", severity="error")







textual_app = ConceptC2Server()

if __name__ == '__main__':
    textual_app.run()