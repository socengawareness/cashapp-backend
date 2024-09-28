# app/main.py
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.database import get_user_by_login_number, update_user_device_id
from app.auth import create_access_token, verify_access_token
from app.models import Login
from datetime import timedelta
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],  # Allow all origins, but you can restrict this to specific domains
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# OAuth2PasswordBearer is used to retrieve the token from the request's Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Dependency: Extract and verify the token
async def get_current_user(token: str = Depends(oauth2_scheme)):
    # Verify and decode the token
    payload = verify_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    # Get the login_number from the token's payload
    login_number = payload.get("sub")
    if login_number is None:
        raise HTTPException(
            status_code=401, detail="Token does not contain user information"
        )
    # Retrieve the user from the database
    user = await get_user_by_login_number(login_number)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@app.post("/login")
async def login(user: Login):
    # Check if the user exists by login number
    print(user)
    db_user = await get_user_by_login_number(user.login_number)

    if db_user:
        # Check if the device_id exists in the database
        print(db_user)
        if "device_id" in db_user:
            # If device_id exists, check if it matches the provided device_id
            if db_user["device_id"] != user.device_id:
                raise HTTPException(
                    status_code=400, detail="You cannot log in on multiple devices"
                )

        else:
            # If device_id does not exist, update the user record with the new device_id
            await update_user_device_id(user.login_number, user.device_id)

        # Generate a JWT token
        access_token_expires = timedelta(hours=24)
        access_token = create_access_token(
            data={"sub": db_user["login_number"]}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}

    raise HTTPException(status_code=400, detail="Invalid login credentials")


@app.get("/get-user")
async def get_user(current_user: dict = Depends(get_current_user)):
    """
    Retrieve user information and check subscription status.
    Requires a valid JWT token.
    """

    # Default subscription details
    subscription = False
    subscription_message = "not subscribed"

    # Check if the user has a subscription start and end date
    subscription_start_date = current_user.get("subscription_start_date")
    subscription_end_date = current_user.get("subscription_end_date")

    if subscription_start_date and subscription_end_date:
        # Convert subscription dates to datetime objects
        # subscription_start_date = datetime.strptime(subscription_start_date, "%Y-%m-%d")
        # subscription_end_date = datetime.strptime(subscription_end_date, "%Y-%m-%d")
        current_date = datetime.utcnow()

        # Check if the subscription is active or expired
        if subscription_start_date <= current_date <= subscription_end_date:
            subscription = True
            subscription_message = "active"
        elif current_date > subscription_end_date:
            subscription = False
            subscription_message = "expired"
    else:
        # No subscription found
        subscription = False
        subscription_message = "not subscribed"

    # Return user data along with subscription status
    return {
        "email": current_user.get("user_email"),
        "login_number": current_user.get("login_number"),
        "subscription": subscription,
        "subscription_message": subscription_message,
    }


# /token endpoint to exchange username/password for a JWT token
@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    # Replace 'username' with 'login_number' as per your app's login logic
    print(form_data.username)
    db_user = await get_user_by_login_number(form_data.username)
    print(db_user["login_number"])
    print(db_user["device_id"])

    if not db_user or db_user["device_id"] != form_data.password:
        raise HTTPException(
            status_code=400, detail="Incorrect login number or password"
        )

    # Generate the JWT token
    access_token_expires = timedelta(hours=24)

    access_token = create_access_token(
        data={"sub": db_user["login_number"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# @app.post("/add_user")
# async def add_user(user: AddUser):
#     # Check if user already exists
#     db_user = await get_user_by_login_number(user.login_number)
#     if db_user:
#         raise HTTPException(status_code=400, detail="User already exists")

#     # Create a new user (without a device_id)
#     new_user_id = await create_user(
#         {
#             "login_number": user.login_number,
#             # Do not store device_id at signup, it will be captured at first login
#         }
#     )

#     return {"message": "User created", "user_id": new_user_id}
