import logging
from fastapi import APIRouter, status, HTTPException, Depends, Response, Request
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from app.schemas import user_schemas
from app.db import connection
from app.core import utils
from app.core import security

router = APIRouter(tags=['Login'])
logger = logging.getLogger(__name__)
cred_error = 'Invalid Credentials'


@router.post("/login",
             summary="Logs in a user, returns a jwt token",
             # response_model=user_schemas.Token,
             status_code=status.HTTP_202_ACCEPTED)
async def login(user_credentials: OAuth2PasswordRequestForm = Depends(),
                database_access: list = Depends(connection.get_db)
                ):
    conn, cursor = database_access
    # OAuth2Password Request Form Returns username and password as a dictionary,
    # in this case the username is the email
    user_email = str(user_credentials.username)

    cursor.execute(f"SELECT * FROM users WHERE email = %s ", (user_email,))
    user = cursor.fetchone()

    if not user:
        logger.error(cred_error)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=cred_error)
    if not await utils.verify_login_details(user_credentials.password, user['password']):
        logger.error(cred_error)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=cred_error)
    access_token = await security.create_access_token(data={'user_id': user['user_id']})
    logger.info(f'User {user['user_id']} logged in')
    user = user_schemas.UserOut(user_id=user['user_id'], email=user['email'], created_date=user['created_date'],
                                first_name=user['first_name'], last_name=user['last_name'])

    token = user_schemas.Token(access_token=access_token, token_type="bearer")
    return user_schemas.Login(user=user, token=token)


@router.get('/me',
            summary="Checks the logged in user's details",
            description="Endpoint to check the user's details",
            status_code=status.HTTP_200_OK,
            )
async def get_current_user(current_user: user_schemas.TokenData = Depends(security.get_current_user)):
    return {'detail': 'user is logged in', 'user_id': current_user.user_id}
