for (i in prev_comments){
	prev_comments[i].draw = prev_comments[i].draw.replace(/&quot;/gmi, '"');
}
localStorage.setItem('comments', JSON.stringify(prev_comments));

function send_data_to_server(){
	comments_to_send = [];
	for (i in comments){
		comment = comments[i];
		if(comment.is_new){
			comments_to_send.push(comment);
		}
	}
	json_to_send = JSON.stringify(comments_to_send);
	const fd = new FormData();
	fd.append('json_string', json_to_send);
	video_url = video.getElementsByTagName('source')[0].getAttribute('src');
	fd.append('video_url', video_url );
	fd.append('session', comment_session_id );
	fd.append('user_id', user_id );
	fd.append('task', task_id );
	fd.append('num', comments_to_send.length);
	const xhr = new XMLHttpRequest();
	xhr.onload = () => {
	if (xhr.status >= 200 && xhr.status < 300) {
		  alert("Комментарии сохранены");
		  comment_session_id = xhr.response;
		} else alert("Что-то пошло не так.\n Ошибка: " + xhr.status);
	};
	adress = '/toonproject/update_comment_session';
	xhr.open('POST', adress, true);
	xhr.send(fd);
}