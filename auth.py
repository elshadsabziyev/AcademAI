import json
import requests
from credential_loader import Credentials
import streamlit as st
import re


class FirebaseAuthenticator(Credentials):

    def __init__(self) -> None:
        super().__init__()
        self.firebase_config = self.get_firebase_config().get("apiKey")

    def sign_in_with_email_and_password(self, email: str, password: str) -> dict:

        request_ref = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key={0}".format(
            self.firebase_config
        )
        headers = {"content-type": "application/json; charset=UTF-8"}
        data = json.dumps(
            {"email": email, "password": password, "returnSecureToken": True}
        )
        request_object = requests.post(request_ref, headers=headers, data=data)
        self.raise_detailed_error(request_object)
        return request_object.json()

    def get_account_info(self, id_token: str) -> dict:

        request_ref = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/getAccountInfo?key={0}".format(
            self.firebase_config
        )
        headers = {"content-type": "application/json; charset=UTF-8"}
        data = json.dumps({"idToken": id_token})
        request_object = requests.post(request_ref, headers=headers, data=data)
        self.raise_detailed_error(request_object)
        return request_object.json()

    def send_email_verification(self, id_token: str) -> dict:

        request_ref = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/getOobConfirmationCode?key={0}".format(
            self.firebase_config
        )
        headers = {"content-type": "application/json; charset=UTF-8"}
        data = json.dumps({"requestType": "VERIFY_EMAIL", "idToken": id_token})
        request_object = requests.post(request_ref, headers=headers, data=data)
        self.raise_detailed_error(request_object)
        return request_object.json()

    def send_password_reset_email(self, email: str) -> dict:

        request_ref = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/getOobConfirmationCode?key={0}".format(
            self.firebase_config
        )
        headers = {"content-type": "application/json; charset=UTF-8"}
        data = json.dumps({"requestType": "PASSWORD_RESET", "email": email})
        request_object = requests.post(request_ref, headers=headers, data=data)
        self.raise_detailed_error(request_object)
        return request_object.json()

    def create_user_with_email_and_password(self, email: str, password: str) -> dict:

        request_ref = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/signupNewUser?key={0}".format(
            self.firebase_config
        )
        headers = {"content-type": "application/json; charset=UTF-8"}
        data = json.dumps(
            {"email": email, "password": password, "returnSecureToken": True}
        )
        request_object = requests.post(request_ref, headers=headers, data=data)
        self.raise_detailed_error(request_object)
        return request_object.json()

    def delete_user_account(self, id_token: str) -> dict:

        request_ref = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/deleteAccount?key={0}".format(
            self.firebase_config
        )
        headers = {"content-type": "application/json; charset=UTF-8"}
        data = json.dumps({"idToken": id_token})
        request_object = requests.post(request_ref, headers=headers, data=data)
        self.raise_detailed_error(request_object)
        return request_object.json()

    def raise_detailed_error(self, request_object: requests.models.Response) -> None:

        try:
            request_object.raise_for_status()
        except requests.exceptions.HTTPError as error:
            raise requests.exceptions.HTTPError(error, request_object.text)

    def sign_in(self, email: str, password: str) -> None:

        try:
            id_token = self.sign_in_with_email_and_password(email, password)["idToken"]
            account_info = self.get_account_info(id_token)
            print(account_info)
            user_info = account_info["users"][0]
            if not user_info["emailVerified"]:
                self.send_email_verification(id_token)
                st.session_state.auth_warning = """
                ##### Email not verified.
                - Check your inbox to verify your email.
                - Please check your spam folder if you don't see it in your inbox.
                """
            else:
                user_info["idToken"] = id_token
                user_info["fullUserInfo"] = account_info
                st.session_state.user_info = user_info
                st.rerun()
        except requests.exceptions.HTTPError as error:
            error_message = json.loads(error.args[1])["error"]["message"]
            if error_message in {
                "INVALID_EMAIL",
                "EMAIL_NOT_FOUND",
                "INVALID_PASSWORD",
                "MISSING_PASSWORD",
                "INVALID_LOGIN_CREDENTIALS",
            }:
                st.session_state.auth_warning = """
                ##### Error: Invalid login credentials.
                - Please check your email and password.
                - Forgot your password?
                - Click the 'Forgot Password' button to reset it.
                """
            elif any(
                re.search(pattern, error_message, re.IGNORECASE)
                for pattern in {
                    "TOO_MANY_ATTEMPTS_TRY_LATER",
                    "USER_DISABLED",
                    "OPERATION_NOT_ALLOWED",
                    "USER_NOT_FOUND",
                    "TOO_MANY_ATTEMPTS_TRY_LATER : Too many unsuccessful login attempts. Please try again later.",
                }
            ):
                st.session_state.auth_warning = """
                ##### Error: Too many attempts.
                - Please try again later.
                - You are temporarily blocked from signing in.
                - Be sure to verify your email.
                - Get access instantly by resetting your password.
                - Or, wait for a while and try again.
                """
            else:
                st.session_state.auth_warning = f"Error: {error_message}"
        except Exception as error:
            st.session_state.auth_warning = f"Error: {error}"

    def create_account(self, email: str, password: str) -> None:

        try:
            id_token = self.create_user_with_email_and_password(email, password)[
                "idToken"
            ]
            self.send_email_verification(id_token)
            st.session_state.auth_success = f"""
            ##### Account created successfully.
            - Email sent to {email} to verify your email.
            - Check your inbox to verify your email.
            - Please check your spam folder if you don't see it in your inbox.
            """
        except requests.exceptions.HTTPError as error:
            error_message = json.loads(error.args[1])["error"]["message"]
            if error_message == "EMAIL_EXISTS":
                st.session_state.auth_warning = """
                    ##### Error: Email already exists.
                    - Use a different email.
                    - If you already have an account, sign in.
                    - Forgot your password?
                    - Click the 'Forgot Password' button to reset it.
                    """
            elif error_message in {
                "INVALID_EMAIL",
                "MISSING_EMAIL",
            }:
                st.session_state.auth_warning = "Error: Use a valid email address"
            elif error_message in {
                "MISSING_PASSWORD",
                "WEAK_PASSWORD : Password should be at least 6 characters",
            }:
                st.session_state.auth_warning = """
                ##### Error: Weak password.
                - Password should be at least 6 characters.
                - Use a strong password.
                - Include numbers, symbols, and uppercase letters.
                """
            else:
                st.session_state.auth_warning = f"Error: {error_message}"
        except Exception as error:
            st.session_state.auth_warning = f"Error: {error}"

    def reset_password(self, email: str) -> None:

        try:
            self.send_password_reset_email(email)
            st.session_state.auth_success = f"""
            ##### Password reset email sent.
            - Email sent to {email} to reset your password.
            - Check your inbox to reset your password.
            - Please check your spam folder if you don't see it in your inbox.
            """
        except requests.exceptions.HTTPError as error:
            error_message = json.loads(error.args[1])["error"]["message"]
            if error_message in {"MISSING_EMAIL", "INVALID_EMAIL", "EMAIL_NOT_FOUND"}:
                st.session_state.auth_warning = """
                ##### Error: Invalid email.
                - Please check your email address.  
                - Use the email address you used to create your account.
                """
            else:
                st.session_state.auth_warning = f"Error: {error_message}"
        except Exception as error:
            st.session_state.auth_warning = f"Error: {error}"

    def sign_out(self) -> None:

        st.session_state.clear()
        st.session_state.auth_success = (
            "user signed out successfully."  # Not displayed in the app
        )

    def delete_account(self, password: str) -> None:

        try:
            id_token = self.sign_in_with_email_and_password(
                st.session_state.user_info["email"], password
            )["idToken"]
            self.delete_user_account(id_token)
            st.session_state.clear()
            st.session_state.auth_success = """
            ##### Account deleted successfully.
            - Your account has been deleted.
            - You have been signed out.
            - Sign up to create a new account.
            """
        except requests.exceptions.HTTPError as error:
            error_message = json.loads(error.args[1])["error"]["message"]
            if error_message in {
                "INVALID_EMAIL",
                "EMAIL_NOT_FOUND",
                "INVALID_PASSWORD",
                "MISSING_PASSWORD",
                "INVALID_LOGIN_CREDENTIALS",
            }:
                st.session_state.auth_warning = f"""
                ##### Error: Invalid login credentials.
                - You have to enter your password again to delete your account.
                - Please check your password.
                - Use the password you used to sign in.
                - Forgot your password?
                - Click the 'Forgot Password' button to reset it.
                """
            elif any(
                re.search(pattern, error_message, re.IGNORECASE)
                for pattern in {
                    "TOO_MANY_ATTEMPTS_TRY_LATER",
                    "USER_DISABLED",
                    "OPERATION_NOT_ALLOWED",
                    "USER_NOT_FOUND",
                    "TOO_MANY_ATTEMPTS_TRY_LATER : Too many unsuccessful login attempts. Please try again later.",
                }
            ):
                st.session_state.auth_warning = """
                ##### Error: Too many attempts.
                - Please try again later.
                - You are temporarily blocked from signing in.
                - Be sure to verify your email.
                - Get access instantly by resetting your password.
                - Or, wait for a while and try again.
                """
            else:
                st.session_state.auth_warning = f"Error: {error_message}"
        except Exception as error:
            st.session_state.auth_warning = f"Error: {error}"

    def verify_password(self, password: str) -> bool:

        try:
            id_token = st.session_state.user_info["idToken"]
            self.sign_in_with_email_and_password(
                st.session_state.user_info["email"], password
            )
            return True
        except requests.exceptions.HTTPError as error:
            error_message = json.loads(error.args[1])["error"]["message"]
            if error_message in {
                "INVALID_EMAIL",
                "EMAIL_NOT_FOUND",
                "INVALID_PASSWORD",
                "MISSING_PASSWORD",
                "INVALID_LOGIN_CREDENTIALS",
            }:
                return False
            elif any(
                re.search(pattern, error_message, re.IGNORECASE)
                for pattern in {
                    "TOO_MANY_ATTEMPTS_TRY_LATER",
                    "USER_DISABLED",
                    "OPERATION_NOT_ALLOWED",
                    "USER_NOT_FOUND",
                    "TOO_MANY_ATTEMPTS_TRY_LATER : Too many unsuccessful login attempts. Please try again later.",
                }
            ):
                return False
            else:
                return False
        except Exception as error:
            return False

    def get_test_user(self):

        return {
            "fullUserInfo": {
                "users": [
                    {
                        "localId": "test_user_id",
                        "email": "test_user_email",
                        "displayName": "Test User",
                        "photoUrl": "https://example.com/test_user_photo.jpg",
                        "emailVerified": True,
                        "providerUserInfo": [
                            {
                                "providerId": "password",
                                "federatedId": "test_user_federated_id",
                                "email": "test_user_email",
                                "displayName": "Test User",
                                "photoUrl": "https://example.com/test_user_photo.jpg",
                                "rawId": "test_user_raw_id",
                            }
                        ],
                        "validSince": "1717877715",
                        "lastLoginAt": "1717886593722",
                        "createdAt": "1717877715170",
                        "lastRefreshAt": "2024-06-08T22:43:13.722Z",
                        "testUser": True,
                    }
                ],
            },
            "idToken": "test_id_token",
        }

    def sign_in_test_user(self):

        st.session_state.user_info = self.get_test_user()
        st.rerun()
