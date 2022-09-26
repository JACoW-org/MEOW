window.addEventListener("DOMContentLoaded", () => {

    const websocket = new WebSocket(`ws://${location.host}/socket/jpsp:feed`);

    websocket.addEventListener('open', function (event) {

        console.log('onopen')

        websocket.addEventListener("message", ({ data }) => {
            // const event = JSON.parse(data);
            console.log(data)
        });

        document.getElementById('task_button').addEventListener("click", () => {
            websocket.send(JSON.stringify({
                event: 'action',
                params: {
                    task: 'xml_merge'
                },
                time: `${new Date().getTime()}`
            }));
        });

        document.getElementById('del_button').addEventListener("click", () => {
            fetch(`http://${location.host}/api/conference/44/del`)
                .then(res => res.json())
                .then(json => console.log(json))
                .catch(err => console.error(err))
        });

        document.getElementById('put_button').addEventListener("click", () => {
            fetch(`http://${location.host}/api/conference/44/put`)
                .then(res => res.json())
                .then(json => console.log(json))
                .catch(err => console.error(err))
        });

        document.getElementById('get_button').addEventListener("click", () => {

            fetch(`http://${location.host}/api/conference/44/get`, {
                headers: {
                    'X-API-Key': '01GDWDBTHHJNZ0KAVKZ1YP320S'
                }
            })
                .then(res => res.json())
                .then(json => console.log(json))
                .catch(err => console.error(err))
        });

        document.getElementById('401_button').addEventListener("click", () => {

            fetch(`http://${location.host}/api/conference/44/get`)
                .then(res => res.json())
                .then(json => console.log(json))
                .catch(err => console.error(err))
        });

        document.getElementById('ab_button').addEventListener("click", () => {
            fetch(`http://${location.host}/api/conference/44/ab.odt`)
                .then(res => res.blob())
                .then(blob => {
                    const a = document.createElement('a');
                    a.href = window.URL.createObjectURL(blob);
                    a.download = "ab.odt";
                    document.body.appendChild(a); // we need to append the element to the dom -> otherwise it will not work in firefox
                    a.click();
                    a.remove();  //afterwards we remove the element again
                })
                .catch(err => console.error(err))
        });


        task_button

    });


});

console.log('start')