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

    var checkDrawed;

    video.ontimeupdate = function() {

        timeShow();

        checkFrame();

    };

    function timeShow() {

        document.getElementById("time").innerHTML = Math.floor(video.currentTime * 25);

    }

    var fps = 25;

    var frameTime = 1 / fps;

    var stepSize = 1;

    var frame = frameTime * stepSize;

    function moveByFramePlus() {
	
        checkDrawed = JSON.parse(localStorage.getItem('comments'));

        var sizeDrawed = checkDrawed.length - 1;

        if (canvas._objects[0] && JSON.parse(checkDrawed[sizeDrawed].draw).objects.length !== canvas._objects.length) {
            addComment();
        }

        video.pause();

        video.currentTime = (video.currentTime + frame).toFixed(7);

        vidUpdate();

        return;

    }

    document.getElementById("frame+1").onclick = moveByFramePlus;

    function moveByFrameMinus() {
        checkDrawed = JSON.parse(localStorage.getItem('comments'));

        var sizeDrawed = checkDrawed.length - 1;

        if (canvas._objects[0] && JSON.parse(checkDrawed[sizeDrawed].draw).objects.length !== canvas._objects.length) {
            addComment();
        }

        video.pause();

        video.currentTime = (video.currentTime - frame).toFixed(7);

        vidUpdate();

        return;

    }

    document.getElementById("frame-1").onclick = moveByFrameMinus;

    var comments = [];

    var comment = {};

    //var today = new Date().toLocaleString();
	
	

    var addComment = function addComment() {
	
		var today = new Date();
	
		canvas.historyInit();

        comment.time = Math.floor(video.currentTime * 25);
        comment.timeAll = video.currentTime;
        comment.user = document.getElementById("user_in").innerText;
        comment.message = document.getElementsByTagName('textarea')[0].value;
        comment.date = today;

        comment.color = '#' + Math.random().toString(16).substr(-6);

        comment.draw = JSON.stringify(canvas.toJSON());

        comments.push(comment);

        localStorage.setItem('comments', JSON.stringify(comments));

        showComments();

        document.getElementsByTagName('textarea')[0].value = "";
        send_data_to_server();
    }

    document.getElementById('add-comment').onclick = addComment;

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
		
    if (canvas.freeDrawingBrush) {
        canvas.freeDrawingBrush.color = drawingColorEl.value;
        canvas.freeDrawingBrush.width = parseInt(drawingLineWidthEl.value);
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
        canvas.freeDrawingBrush.width = parseInt(this.value);
        document.getElementsByClassName('lineWidth')[0].innerHTML = this.value;
    };

    var shower = 1;

    function showComments() {

        if (localStorage.getItem('comments')) {

            comments = JSON.parse(localStorage.getItem('comments'));

            document.getElementById('comments').innerHTML = "";
            document.getElementById('frames').innerHTML = "";
			
			

            if (shower === 1 && document.getElementById('byFrame').getAttribute('state') == "true") {
			
                
				//comments 
				
				//= comments.reverse();
				
				
				              comments = comments.sort(function(a, b) {
                    //return a.time - b.time
					
					return new Date(a.date) - new Date(b.date);
                });
				
				document.getElementById('byFrame').setAttribute('state', "false")
				
				
            } else if (shower === 1 && document.getElementById('byFrame').getAttribute('state') == "false")
			
			{//comments = comments.reverse();
			
						              comments = comments.sort(function(a, b) {
                    //return b.time - a.time
					
					return new Date(b.date) - new Date(a.date);
                });
			
			
			document.getElementById('byFrame').setAttribute('state', "true")}
			
			else if (shower === 2 && document.getElementById('byAdd').getAttribute('state') == "true")
			{
                comments = comments.sort(function(a, b) {
                    return a.time - b.time
					
					//return new Date(a.date) - new Date(b.date);
                });
				
				document.getElementById('byAdd').setAttribute('state', "false")
            }
			
			else if (shower === 2 && document.getElementById('byAdd').getAttribute('state') == "false")
			{
                    comments = comments.sort(function(a, b) {
                    return b.time - a.time
					
					//return new Date(b.date) - new Date(a.date);
					
                }); document.getElementById('byAdd').setAttribute('state', "true")
            }
			


            for (var c = 0; c < comments.length; c++) {

                var transform = comments[c].time * 960 / Math.floor(video.duration * 25);

                document.getElementById('frames').innerHTML += '<div onclick="showDraw(this)" sid=' + c + ' class="frames" style="transform: translate3d(' + parseInt(transform) + 'px, 0px, 0px);background: ' + comments[c].color + '"></div>'

                document.getElementById('comments').innerHTML += "<div class='comment'><div style='width:240px;float:left;color:#fff'><i class='fas fa-circle' style='color:" + comments[c].color + ";'></i> " + comments[c].user + "<span><i class='fas fa-history'></i> " + comments[c].time + "</span></div><button class='btn btn-default' style='float:right;line-height:26px;position:relative;z-index: 99' sid=" + c + "><i class='fas fa-times'></i></button></div><div class='commentText' onclick='showDraw(this)' sid=" + c + " >" + comments[c].message + "</div><div style='width:100%;height:30px;line-height:30px;float:left;color:#fff;border:1px solid #282828;border-top:0;padding-left:10px;font-size:12px;'>Добавлено: " + new Date(comments[c].date).toLocaleString(); + "</div>"

            }
			


        }
		
		

    }

    window.onload = function() {

        showComments()

    }

    //var click = 0;

    function showDraw(e) {
	
		canvas.historyInit();
	
        state = 1;

        var c = e.getAttribute('sid');

        video.pause();
        video.currentTime = comments[c].timeAll;

        vidUpdate();
		
		

    }

    function deleteComment(e) {

        var c = e.getAttribute('sid');

        var commentsStorage = JSON.parse(localStorage.getItem('comments'));

        commentsStorage = commentsStorage.splice(c, 1);

        localStorage.setItem('comments', JSON.stringify(commentsStorage));

        location.reload();

    }

    function checkFrame() {

        canvas.clear();
        canvas.calcOffset();
        canvas.renderAll();

        var drawComments = JSON.parse(localStorage.getItem('comments'));

        if (localStorage.getItem('comments')) {

            for (var c = 0; c < drawComments.length; c++) {

                if (Math.floor(drawComments[c].time / 1) == Math.floor(video.currentTime * 25)) {

                    canvas.loadFromJSON(drawComments[c].draw);

                    canvas.calcOffset();
                    canvas.renderAll();

                }

            }

        }

    }

	
	
	//var history;
	//array.reverse()  

    fabric.Canvas.prototype.historyInit = function() {
        this.historyUndo = [];
        this.historyNextState = this.historyNext();

        this.on({
            //"object:added": this.historySaveAction,
            "object:removed": this.historySaveAction,
            //"object:modified": this.historySaveAction,
			'path:created': this.historySaveAction
        })
		
		//return this.historyUndo;
		
		
		
    }

    fabric.Canvas.prototype.historyNext = function() {
        return JSON.stringify(this.toDatalessJSON(this.extraProps));
    }

    fabric.Canvas.prototype.historySaveAction = function() {
        if (this.historyProcessing)
            return;

        const json = this.historyNextState;
        this.historyUndo.push(json);
		
		//historyUndo.push(json);
		
        this.historyNextState = this.historyNext();
    }


    fabric.Canvas.prototype.undo = function() {
	
		//console.log(this.historyUndo);
		
		//console.log(history);
        
		this.historyProcessing = true;

		const history = this.historyUndo.pop();
		
		//history = this.historyUndo.pop();
        
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

    /*function KeyPress(e) {

        e = e || window.event;

        if ((e.which == 90 || e.keyCode == 90) && e.ctrlKey) {
            //canvas.undo();
        }
    }*/

    document.onkeydown = checkKey;

    function checkKey(e) {

        e = e || window.event;

        //if ((e.which == 90 || e.keyCode == 90) && e.ctrlKey) {
        //    canvas.undo();
        //} else 
		
		
		if (e.keyCode == '32' && document.activeElement.tagName !== 'TEXTAREA') {

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

            canvas.freeDrawingBrush.width = 20;

            //eraser
            canvas.on('path:created', function(opt) {
                opt.path.globalCompositeOperation = 'destination-out';
                opt.path.lineWidth = 20;
                opt.color = drawingColorEl.value;
                canvas.requestRenderAll();
            });

        } else {

            canvas.freeDrawingBrush.width = parseInt(drawingLineWidthEl.value);

            //draw
            canvas.on('path:created', function(opt) {
                opt.path.globalCompositeOperation = 'source-over';
                opt.color = drawingColorEl.value;
                canvas.requestRenderAll();

            });

        }

    }

    function canvasDisplay() {

        document.getElementById('check1').checked == false ? document.getElementsByClassName('canvas-container')[0].style.display = 'none' : document.getElementsByClassName('canvas-container')[0].style.display = 'block'

    }