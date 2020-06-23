document.addEventListener('DOMContentLoaded', () => {

    // Connect to websocket
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    // When connected, configure button
    socket.on('connect', () => {

        // Notify the server user has joined
        socket.emit('joined');

        // Forget user's last channel when clicked on '+ Channel'
        document.querySelector('#newChannel').addEventListener('click', () => {
            localStorage.removeItem('last_channel');
        });
        

        // Forget user's last channel when logged out
        document.querySelector('#logout').addEventListener('click', () => {
            localStorage.removeItem('last_channel');
        });

        // 'Enter' key on textarea also sends a message
        // https://developer.mozilla.org/en-US/docs/Web/Events/keydown
        document.querySelector('#myMessage').addEventListener("keydown", event => {
            if (event.key == "Enter") {
                document.getElementById("sendmessage").click();
            }
        });
        
        // Send button emits a "message sent" event
        document.querySelector('#sendmessage').addEventListener("click", () => {
            
            // Save time in format HH:MM:SS
            let timestamp = new Date;
            timestamp = timestamp.toLocaleTimeString();

            // Save user input
            let msg = document.getElementById("myMessage").value;

            socket.emit('send message', msg, timestamp);
            
            // Clear input
            document.getElementById("myMessage").value = '';
        });
    });
    
    // When user joins a channel, add a message and on users connected.
    socket.on('status', data => {

        // Broadcast message of joined user.
        
        $( 'div.message_holder' ).append( '<div class="msg_bbl"><b style="color: #000" style="width:100%;">'+data.msg+'</b> </div>')
        scrollDownChatWindow() 
        // Save user current channel on localStorageq
        localStorage.setItem('last_channel', data.channel)
    })

    // When a message is announced, add it to the textarea.
    socket.on('announce message', data => {

        $( 'div.message_holder' ).append( '<div class="msg_bbl"><b style="color: #000" style="width:100%;">'+data.user+'</b> '+data.msg+'</br>'+data.timestamp+'</div>' )
        scrollDownChatWindow() 
        
    })

    function scrollDownChatWindow() {
        const chatWindow = document.querySelector(".message_holder");
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }

    
});