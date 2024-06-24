from credential_loader import Credentials
import firebase
import streamlit as st


class RealtimeDB(Credentials):
    def __init__(self) -> None:
        super().__init__()
        try:
            self.app = firebase.initialize_app(self.firebase_config)
        except Exception as e:
            st.error(
                f"""
                # There was an error initializing the Firebase app.
                - You may want to refresh the page.
                - If the problem persists, please contact the developer.
                """
                + str(e)
            )
            st.stop()
        if st.session_state.get("user_info") is not None:
            self.db = self.app.database()
            self.user_info = st.session_state.user_info["fullUserInfo"]
            self.id_token = st.session_state.user_info["idToken"]

    def push_chat_message_for_user(self, user_id: str, message: dict) -> None:
        try:
            self.db.child("users").child(user_id).child("chat_history").push(
                data=message, token=self.id_token
            )
        except Exception as e:
            st.error(
                f"""
                # There was an error storing the chat message.
                - You may want to refresh the page.
                - If the problem persists, please contact the developer.
                """
            )

    def fetch_user_chat_history(self) -> dict:
        try:
            uid = self.user_info["users"][0]["localId"]
            return (
                self.db.child("users")
                .child(uid)
                .child("chat_history")
                .get(token=self.id_token)
                .val()
            )
        except Exception as e:
            st.error(
                f"""
                # There was an error getting the chat messages.
                - You may want to refresh the page.
                - If the problem persists, please contact the developer.
                """
            )
            st.stop()

    def delete_user_chat_history(self) -> None:
        try:
            uid = self.user_info["users"][0]["localId"]
            self.db.child("users").child(uid).child("chat_history").remove(
                token=self.id_token
            )
        except Exception as e:
            st.error(
                f"""
                # There was an error clearing the chat history.
                - You may want to refresh the page.
                - If the problem persists, please contact the developer.
                """
            )
            st.stop()

    class Storage:
        def __init__(self, db: firebase.database.Database, id_token: str) -> None:
            self.db = db
            self.id_token = id_token

        def store_image(self, image: bytes, user_id: str) -> str:
            try:
                image_url = (
                    self.db.child("images")
                    .child(user_id)
                    .put(image, token=self.id_token)
                )
                return image_url
            except Exception as e:
                st.error(
                    f"""
                    # There was an error storing the image.
                    - You may want to refresh the page.
                    - If the problem persists, please contact the developer.
                    """
                )
                st.stop()

        def fetch_image(self, image_url: str) -> bytes:
            try:
                image = (
                    self.db.child("images").child(image_url).get(token=self.id_token)
                )
                return image
            except Exception as e:
                st.error(
                    f"""
                    # There was an error fetching the image.
                    - You may want to refresh the page.
                    - If the problem persists, please contact the developer.
                    """
                )
                st.stop()
