import bcrypt
import pandas as pd
import streamlit as st
import streamlit_authenticator as stauth


def hash_password(password):
    """
    Hashes a password using bcrypt with a salt.
    """
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def authenticate_user(users_df):
    """
    handles user authentication using Streamlit Authenticator.
    """
    users_df = users_df.dropna(subset=users_df.columns)
    if 'Hashed_Password' not in users_df.columns:
        users_df['Hashed_Password'] = users_df['Password'].astype(str).apply(hash_password)

    names = list(users_df['Name'].str.strip())
    usernames = list(users_df['Email'].str.strip())
    passwords = list(users_df['Hashed_Password'].str.strip())

    authenticator = stauth.Authenticate(
        names,
        usernames,
        passwords,
        cookie_name='leads-cookie',
        key='cookie',
        cookie_expiry_days=1
    )

    name, authentication_status, username = authenticator.login('Login', 'main')
    st.session_state.authentication_status = authentication_status

    return authenticator, authentication_status, name, username


def handle_authentication_status(authenticator, authentication_status, name):
    """
    handles the display of the authentication state.
    """
    if authentication_status:
        with st.sidebar:
            st.write(f"Welcome {name}")
            try:
                if authenticator.logout("Logout", location='main'):
                    st.session_state.authentication_status = None
                    st.rerun()
            except KeyError:
                st.session_state.authentication_status = None
                st.rerun()
                pass
            except Exception as err:
                st.session_state.authentication_status = None
                st.error(f'Unexpected exception {err}')
                raise Exception(err)
    elif authentication_status is False:
        st.error('Username/password is incorrect')
    elif authentication_status is None:
        pass
        # st.warning('Please enter your username and password')
