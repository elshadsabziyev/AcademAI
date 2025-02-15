import time
import streamlit as st
from auth import FirebaseAuthenticator
from db import RealtimeDB


class App(FirebaseAuthenticator, RealtimeDB):
    def __init__(self):
        super().__init__()
        self.set_page_config()

    def set_page_config(self):
        st.set_page_config(
            page_title="AcademAI",
            page_icon="📚",
            layout="wide",
            initial_sidebar_state="auto",
        )

    def auth_page(self):
        if "user_info" not in st.session_state:
            col1, col2, col3 = st.columns([2, 5, 2])
            login_register = col2.toggle(
                label="**Login/Register**", key="login_register"
            )
            if login_register:
                do_you_have_an_account = "No"
            else:
                do_you_have_an_account = "Yes"
            auth_form = col2.form(key="Authentication form", clear_on_submit=False)
            email = auth_form.text_input(
                label="**Email**",
                type="default",
                placeholder="Enter your email",
                autocomplete="email",
            )
            password = (
                auth_form.text_input(
                    label="**Password**",
                    type="password",
                    placeholder="Enter your password",
                    autocomplete="current-password",
                )
                if do_you_have_an_account in {"Yes", "No"}
                else auth_form.empty()
            )
            auth_notification = col2.empty()

            if do_you_have_an_account == "Yes":
                if auth_form.form_submit_button(
                    label="Sign In", use_container_width=True, type="primary"
                ):
                    with auth_notification, st.spinner("Signing in"):
                        self.sign_in(email, password)

                if auth_form.form_submit_button(
                    label="Forgot Password", use_container_width=True, type="secondary"
                ):
                    with auth_notification, st.spinner("Sending password reset link"):
                        self.reset_password(email)
                if auth_form.form_submit_button(
                    label="Continue as Guest",
                    use_container_width=True,
                    type="secondary",
                ):
                    self.sign_in_test_user()
            elif do_you_have_an_account == "No" and auth_form.form_submit_button(
                label="Create Account", use_container_width=True, type="primary"
            ):
                with auth_notification, st.spinner("Creating account"):
                    self.create_account(email, password)

            if "auth_success" in st.session_state:
                auth_notification.success(st.session_state.auth_success)
                del st.session_state.auth_success
            elif "auth_warning" in st.session_state:
                auth_notification.error(st.session_state.auth_warning)
                del st.session_state.auth_warning

        else:
            self.home_page()

    def home_page(self):
        self.sidebar()
        try:
            if (
                st.session_state.user_info["fullUserInfo"]["users"][0]["localId"]
                != "test_user_id"
                and st.session_state.user_info["fullUserInfo"]["users"][0]["email"]
                != "test_user_email"
                and st.session_state.user_info["idToken"] != "test_id_token"
            ):
                st.title(
                    f"**Welcome, _{st.session_state.user_info['fullUserInfo']['users'][0]['email'].split('@')[0]}_!**"
                )
            else:
                st.title("**Welcome, Guest!**")
                st.warning(
                    """
                    # You are currently in guest mode.
                    - Sign in to access your account.
                    - You can still add items to your cart and browse the store.
                    """
                )
        except:
            st.title("**Welcome!**")
        st.info(
            """
            # AcademAI
            """
        )

    def sidebar(self):
        st.sidebar.write("# Your Account")

        if st.sidebar.button("**Sign Out**"):
            session_state_variables = [
                "user_info",
                "delete_account_warning_shown",
                "delete_account_clicked",
                "auth_success",
                "auth_warning",
                "auth_error",
            ]

            for var in session_state_variables:
                try:
                    del st.session_state[var]
                except KeyError:
                    continue
            st.sidebar.success(
                """
                    ##### Signed out successfully.
                    - You have been signed out.
                    - Sign in to access your account.
                    """
            )
            time.sleep(2)
            st.rerun()
        if (
            st.session_state.user_info["fullUserInfo"]["users"][0]["localId"]
            != "test_user_id"
            and st.session_state.user_info["fullUserInfo"]["users"][0]["email"]
            != "test_user_email"
            and st.session_state.user_info["idToken"] != "test_id_token"
        ):
            with st.sidebar.expander("**Premium Access**"):
                st.write(
                    f"**Email:** {st.session_state.user_info['fullUserInfo']['users'][0]['email']}"
                )
                st.success(f"""### Your account has premium access, this includes:""")
                st.success(
                    """ 
                    - *Subcrition Plan: Base ($9.99/month)* \n
                    - Chat with the AI assistant.\n
                    - Premnium Support.\n
                    **More features coming soon!**
                    """
                )
        else:
            with st.sidebar.expander("**Guest Access**"):

                st.warning(f"""### Your are in guest mode""")
                st.warning(
                    """ 
                    - *Subcrition Plan: Guest (Free)* \n
                    - No AI assistant chat.\n
                    - No premium support.\n
                    - Just UI/UX experience.\n
                    **Upgrade to premium for more features!**
                    """
                )
        if (
            st.session_state.user_info["fullUserInfo"]["users"][0]["localId"]
            != "test_user_id"
            and st.session_state.user_info["fullUserInfo"]["users"][0]["email"]
            != "test_user_email"
            and st.session_state.user_info["idToken"] != "test_id_token"
        ):
            with st.sidebar.expander("**Click for Account Settings**"):
                self.account_settings()

        st.sidebar.info(
            """
        # About
        - Made with ❤️ by [AcademAI](#)
        """
        )

    def account_settings(self):
        with st.form(key="delete_account_form", clear_on_submit=True):
            st.subheader("Delete Account:")
            password = st.text_input("**Enter your password**", type="password")
            submit_button = st.form_submit_button(label="**Confirm Delete Account**")
            if submit_button:
                if st.session_state.get("delete_account_warning_shown", False):
                    # Verify the password again before deleting the account
                    if self.verify_password(password):
                        with st.spinner("Deleting account"):
                            self.delete_account(password)
                        if "auth_success" in st.session_state:
                            st.success(st.session_state.auth_success)
                            del st.session_state.auth_success
                            time.sleep(2)
                            st.rerun()
                        elif "auth_warning" in st.session_state:
                            st.error(st.session_state.auth_warning)
                            del st.session_state.auth_warning
                        st.session_state.delete_account_clicked = False
                        st.session_state.delete_account_warning_shown = False
                    else:
                        st.error(
                            """Incorrect password, or too many attempts. Please try again."""
                        )
                else:
                    # Verify the password when the user first enters it
                    if self.verify_password(password):
                        st.warning(
                            "Are you sure you want to delete your account? This action cannot be undone! If you are sure, please retype your password and click the button again."
                        )
                        st.session_state.delete_account_warning_shown = True
                    else:
                        st.error("Incorrect password. Please try again.")
        with st.form(key="Reset", clear_on_submit=True):
            st.subheader("Reset Password:")
            st.info(
                "After clicking the button below, a password reset link will be sent to your email address."
            )
            submit_button = st.form_submit_button(label="**Reset Password**")
            if submit_button:
                with st.spinner("Resetting password"):
                    self.reset_password(
                        st.session_state.user_info["fullUserInfo"]["users"][0]["email"]
                    )
                if "auth_success" in st.session_state:
                    st.success(st.session_state.auth_success)
                    del st.session_state.auth_success
                elif "auth_warning" in st.session_state:
                    st.error(st.session_state.auth_warning)
                    del st.session_state.auth_warning


if __name__ == "__main__":
    app = App()
    app.auth_page()
