import requests
import streamlit as st


MONDAY_API_URL = "https://api.monday.com/v2"
MONDAY_API_TOKEN = st.secrets["MONDAY_API_KEY"]


class MondayTool:

    def __init__(self):
        if not MONDAY_API_TOKEN:
            raise ValueError("MONDAY_API_TOKEN not found in .env file")

        self.headers = {
            "Authorization": MONDAY_API_TOKEN,
            "Content-Type": "application/json"
        }

    def execute_query(self, query: str):
        print("\n[Tool Call] Monday API Query Executed\n")

        response = requests.post(
            MONDAY_API_URL,
            headers=self.headers,
            json={"query": query}
        )

        if response.status_code != 200:
            raise Exception(f"Monday API Error: {response.text}")

        return response.json()

    def get_all_board_items(self, board_id: int):
        all_items = []
        cursor = None

        while True:
            if cursor:
                cursor_part = f', cursor: "{cursor}"'
            else:
                cursor_part = ""

            query = f"""
            query {{
            boards(ids: {board_id}) {{
                items_page(limit: 100{cursor_part}) {{
                cursor
                items {{
                    id
                    name
                    column_values {{
                    id
                    type
                    text
                    value
                    }}
                }}
                }}
            }}
            }}
            """

            result = self.execute_query(query)

            page = result["data"]["boards"][0]["items_page"]

            all_items.extend(page["items"])

            cursor = page.get("cursor")

            if not cursor:
                break

        return all_items