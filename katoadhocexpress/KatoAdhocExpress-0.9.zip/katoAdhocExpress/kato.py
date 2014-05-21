def setInfo(res, skey, exp, user_id, user_name, room_id, room_name, user_email='', welcome_text='', welcome_robot_name=''):
	from datetime import datetime, timedelta
	import jwt, json
	
	expDate = datetime.now() + timedelta(seconds=exp)
	
	payload = '{"exp":'+str(expDate.timestamp())+',"user_id":"'+user_id+'","user_name":"'+user_name+'","room_id":"'+room_id+'","room_name":"'+room_name+'","user_email":"'+user_email+'","welcome_text":"'+welcome_text+'","user_name":"'+user_name+'","room_id":"'+room_id+'","room_name":"'+room_name+'","user_email":"'+user_email+'","welcome_text":"'+welcome_text+'","welcome_robot_name":"'+welcome_robot_name+'"}';
	
	generatedJWT = jwt.encode(json.loads(payload), skey, "HS256")
	jwtToString = generatedJWT.decode()
	
	res.set_cookie( 'KATO_ADHOC_TOKEN', jwtToString )