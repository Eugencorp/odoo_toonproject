var video = document.getElementById("video"),
	play = document.getElementsByClassName('video__play')[0],
	timeline = document.getElementsByClassName('timeline')[0],
	timelineProgress = document.getElementsByClassName('timeline__progress')[0],
	drag = document.getElementsByClassName('timeline__drag')[0];

// Toggle Play / Pause
play.addEventListener('click', togglePlay, false);

function togglePlay() {
	
	if (video.paused == true) {

		document.getElementById("pp").innerHTML = "<i class='fas fa-pause'></i>"

		video.play();

		canvas.clear();
		canvas.calcOffset();
		canvas.renderAll();

	} else if (video.paused == false) {

		document.getElementById("pp").innerHTML = "<i class='fas fa-play'></i>"

		video.pause();

	}
}

// on interaction with video controls
video.onplay = function() {
	TweenMax.ticker.addEventListener('tick', vidUpdate);

};
video.onpause = function() {
	TweenMax.ticker.removeEventListener('tick', vidUpdate);
};
video.onended = function() {
	TweenMax.ticker.removeEventListener('tick', vidUpdate);
};

// Sync the timeline with the video duration
function vidUpdate() {
	TweenMax.set(timelineProgress, {
		//scaleX: (video.currentTime / video.duration).toFixed(5)

		scaleX: (video.currentTime / video.duration)

	});
	TweenMax.set(drag, {
		//x: (video.currentTime / video.duration * timeline.offsetWidth).toFixed(4)
		x: (video.currentTime / video.duration * timeline.offsetWidth)

	});
}

// Make the timeline draggable
Draggable.create(drag, {
	type: 'x',
	trigger: timeline,
	bounds: timeline,
	onPress: function(e) {
		video.currentTime = this.x / this.maxX * video.duration;
		TweenMax.set(this.target, {
			x: this.pointerX - timeline.getBoundingClientRect().left
		});
		this.update();
		var progress = this.x / timeline.offsetWidth;
		TweenMax.set(timelineProgress, {
			scaleX: progress
		});
	},
	onClick: function(e) {

		console.log(this);

		video.currentTime = this.x / this.maxX * video.duration;
		TweenMax.set(this.target, {
			x: this.pointerX - timeline.getBoundingClientRect().left
		});
		this.update();
		var progress = this.x / timeline.offsetWidth;
		TweenMax.set(timelineProgress, {
			scaleX: progress
		});
	},
	onDrag: function() {
		video.currentTime = this.x / this.maxX * video.duration;
		var progress = this.x / timeline.offsetWidth;
		TweenMax.set(timelineProgress, {
			scaleX: progress
		});
	},
	onRelease: function(e) {
		e.preventDefault();
	}
});

video.ontimeupdate = function() {
	
	timeShow();

	checkFrame();

};

function timeShow() {

	document.getElementById("time").innerHTML = (Math.floor(video.currentTime * 25));

	// document.getElementById("time").innerHTML = video.currentTime / 60;
	// document.getElementById("time").innerHTML += "/" + video.duration / 60;

}

var fps = 25;

var frameTime = 1 / fps;

var stepSize = 1;

var frame = frameTime * stepSize;

function moveByFramePlus() {

	video.pause();

	vidUpdate();

	video.currentTime = (video.currentTime + frame);

	return;

}

document.getElementById("frame+1").onclick = moveByFramePlus;

function moveByFrameMinus() {

	video.pause();

	vidUpdate();

	video.currentTime = (video.currentTime - frame);

	return;

}

document.getElementById("frame-1").onclick = moveByFrameMinus;

var comments = [];

var today = new Date();

document.getElementById('add-comment').onclick = function addComment() {

	var comment = {};

	comment.time = video.currentTime;
	comment.user = document.getElementById("user_in").innerText;
	comment.message = document.getElementsByTagName('textarea')[0].value;

	comment.draw = JSON.stringify(canvas.toJSON());

	comment.is_new = true;

	comments.push(comment);

	localStorage.setItem('comments', JSON.stringify(comments));

	canvas.clear();
	canvas.calcOffset();
	canvas.renderAll();

	showComments();

	document.getElementsByTagName('textarea')[0].value = "";
	
	send_data_to_server();

}

var $ = function(id) {
	return document.getElementById(id)
};

var canvas = this.__canvas = new fabric.Canvas('c', {
	isDrawingMode: true
});

fabric.Object.prototype.transparentCorners = false;

var drawingModeEl = $('drawing-mode'),
	drawingOptionsEl = $('drawing-mode-options'),
	drawingColorEl = $('drawing-color'),
	drawingShadowColorEl = $('drawing-shadow-color'),
	drawingLineWidthEl = $('drawing-line-width'),
	drawingShadowWidth = $('drawing-shadow-width'),
	drawingShadowOffset = $('drawing-shadow-offset');
//clearEl = $('clear-canvas');

//clearEl.onclick = function() {
//    canvas.clear()
//};

if (canvas.freeDrawingBrush) {
	canvas.freeDrawingBrush.color = drawingColorEl.value;
	canvas.freeDrawingBrush.width = parseInt(drawingLineWidthEl.value, 10) || 1;
	canvas.freeDrawingBrush.shadow = new fabric.Shadow({
		blur: 0,
		offsetX: 0,
		offsetY: 0,
		affectStroke: true,
		color: 0,
	});
}

drawingColorEl.onchange = function() {
	canvas.freeDrawingBrush.color = this.value;
};

drawingLineWidthEl.onchange = function() {
	canvas.freeDrawingBrush.width = parseInt(this.value, 10) || 1;
	document.getElementsByClassName('lineWidth')[0].innerHTML = this.value;
};

var shower = 1;

function showComments() {

	if (localStorage.getItem('comments')) {

		comments = JSON.parse(localStorage.getItem('comments'));

		document.getElementById('comments').innerHTML = "";

		//var t = 2.451877 * 958 / video.duration;

		//TweenMax.set(timelineProgress, {
		//            scaleX: t / timeline.offsetWidth
		//        });

		if (shower === 1) {
			comments = comments.reverse();
		} else {
			comments = comments.sort(function(a, b) {
				return a.time - b.time
			});
		}

		for (var c = 0; c < comments.length; c++) {

			var transform = comments[c].time * 1280 / video.duration;

			console.log(transform.toFixed(3));

			document.getElementById('frames').innerHTML += '<div onclick="show(this)" sid=' + c + ' class="frames" style="transform: translate3d(' + transform + 'px, 0px, 0px);"></div>'

            document.getElementById('comments').innerHTML += "<div class='comment'><div style='width:240px;float:left;'><i class='fas fa-circle' style='color:red;'></i> " + comments[c].user + "<span><i class='fas fa-stopwatch'></i> " + Math.floor(comments[c].time * 25) + "</span></div><button class='btn btn-default' style='float:right;line-height:36px;position:relative;z-index: 99'><i class='fas fa-times'></i></button></div><div class='commentText' onclick='show(this)' sid=" + c + " >" + comments[c].message + "</div>"

		}

	}

}

window.onload = function() {

	showComments()

}

function show(e) {

	var c = e.getAttribute('sid');

	canvas.loadFromJSON(comments[c].draw);
	canvas.renderAll();
	canvas.calcOffset();

	video.pause();

	video.currentTime = comments[c].time;

	vidUpdate();

}

function checkFrame() {

	canvas.clear();
	canvas.calcOffset();
	canvas.renderAll();

	if (localStorage.getItem('comments')) {

		for (var c = 0; c < comments.length; c++) {

			//parseInt(video.currentTime)+1 == parseInt(comments[c].time) || parseInt(video.currentTime)-1 == parseInt(comments[c].time) ||  

			//if (parseInt(video.currentTime)-1 <= parseInt(comments[c].time) <= parseInt(video.currentTime)+1){

			console.log(Math.floor(comments[c].time * 25));
			console.log(Math.floor(video.currentTime * 25));

			if ( Math.floor(comments[c].time * 25) === Math.floor(video.currentTime * 25) ) {

				console.log(true);

				canvas.loadFromJSON(comments[c].draw);

				canvas.renderAll();
				canvas.calcOffset();

				//timetoClear = parseInt(comments[c].time);

			}

		}

	}

}

fabric.Canvas.prototype.historyInit = function() {
	this.historyUndo = [];
	this.historyNextState = this.historyNext();

	this.on({
		"object:added": this.historySaveAction,
		"object:removed": this.historySaveAction,
		"object:modified": this.historySaveAction
	})
}

fabric.Canvas.prototype.historyNext = function() {
	return JSON.stringify(this.toDatalessJSON(this.extraProps));
}

fabric.Canvas.prototype.historySaveAction = function() {
	if (this.historyProcessing)
		return;

	const json = this.historyNextState;
	this.historyUndo.push(json);
	this.historyNextState = this.historyNext();
}

fabric.Canvas.prototype.undo = function() {
	// The undo process will render the new states of the objects
	// Therefore, object:added and object:modified events will triggered again
	// To ignore those events, we are setting a flag.
	this.historyProcessing = true;

	const history = this.historyUndo.pop();
	if (history) {
		this.loadFromJSON(history).renderAll();
	}

	this.historyProcessing = false;
}

canvas.historyInit();

document.addEventListener('keydown', function(event) {

	if (event.keyCode === 90 && event.ctrlKey) {
		canvas.undo();
	} else if (event.which === 90 && event.ctrlKey) {
		canvas.undo();
	} else if (event.ctrlKey && event.key === 'z') {
		canvas.undo();
	}

});

function KeyPress(e) {

	e = e || window.event;

	if ((e.which == 90 || e.keyCode == 90) && e.ctrlKey) {
		canvas.undo();
	}
}

document.onkeydown = checkKey;

function checkKey(e) {

	e = e || window.event;

	if (e.keyCode == '32' && document.activeElement.tagName !== 'TEXTAREA') {

		console.log(true);
		
		document.activeElement.blur();

		togglePlay();
			
	   

	} else if (e.keyCode == '38') {
		// up arrow
	   // togglePlay();
	} else if (e.keyCode == '40') {
		// down arrow
		//togglePlay();
	} else if (e.keyCode == '37') {
		// left arrow
		moveByFrameMinus();
	} else if (e.keyCode == '39') {
		// right arrow
		moveByFramePlus();
	}

}

var eraser = false;

function erase() {

	if (eraser == true) {

		//eraser
		canvas.on('path:created', function(opt) {
			opt.path.globalCompositeOperation = 'destination-out';
			opt.path.lineWidth = parseInt(drawingLineWidthEl.value, 10) || 2;;
			//opt.path.stroke = 'rgba(0,0,0,0)';
			opt.color = drawingColorEl.value;
			//opt.path.fill = 'black';
			canvas.requestRenderAll();
		});

	} else {

		//draw
		canvas.on('path:created', function(opt) {
			opt.path.globalCompositeOperation = 'source-over';
			opt.path.lineWidth = parseInt(drawingLineWidthEl.value, 10) || 2;
			//opt.path.stroke = 'black';
			//opt.path.fill = 'black';
			opt.color = drawingColorEl.value;
			canvas.requestRenderAll();

		});

	}

}

function canvasDisplay() {

	document.getElementById('check1').checked == false ? document.getElementsByClassName('canvas-container')[0].style.display = 'none' : document.getElementsByClassName('canvas-container')[0].style.display = 'block'

}