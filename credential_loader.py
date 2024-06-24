import streamlit as st


class Credentials:
    def __init__(self) -> None:
        try:
            self.firebase_config = self.get_firebase_config()
        except KeyError:
            st.error(
                """
                # There was an error retrieving the Firebase configuration.
                - Please check the secrets file.
                - If the problem persists, please contact the developer.
                """
            )
        try:
            self.togetherai_credentials = self.get_togetherai_credentials()
        except KeyError:
            st.error(
                """
                # There was an error retrieving the TogetherAI API key.
                - Please check the secrets file.
                - If the problem persists, please contact the developer.
                """
            )
        try:
            self.db_url = st.secrets["firebase_config"]["databaseURL"]
        except KeyError:
            st.error(
                """
                # There was an error retrieving the Firebase database URL.
                - Please check the secrets file.
                - If the problem persists, please contact the developer.
                """
            )

    def get_togetherai_credentials(self) -> dict:
        return st.secrets["togetherai"]["api_key"]

    def get_firebase_config(self) -> dict:
        return {
            "apiKey": st.secrets["firebase_config"]["apiKey"],
            "authDomain": st.secrets["firebase_config"]["authDomain"],
            "projectId": st.secrets["firebase_config"]["projectId"],
            "storageBucket": st.secrets["firebase_config"]["storageBucket"],
            "messagingSenderId": st.secrets["firebase_config"]["messagingSenderId"],
            "appId": st.secrets["firebase_config"]["appId"],
            "measurementId": st.secrets["firebase_config"]["measurementId"],
            "databaseURL": st.secrets["firebase_config"]["databaseURL"],
        }
