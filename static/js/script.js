window.addEventListener("DOMContentLoaded", () => {

    const ulid = ULID();

    document.cookie = 'X-API-Key=01GDWDBTHHJNZ0KAVKZ1YP320S' + '; path=/';

    const websocket = new WebSocket(`ws://${location.host}/socket/jpsp:feed`);

    const store = {};

    websocket.addEventListener('open', function (event) {

        console.log('onopen')

        websocket.addEventListener("message", ({ data }) => {
            // const event = JSON.parse(data);

            data = JSON.parse(data)

            console.log(data)

            if (data && data.head)

                store[data.head.uuid] = store[data.head.uuid] || {};

            if (['task:queued'].includes(data.head.code)) {

                store[data.head.uuid].queued_time = data.head.time;

            } else if (['task:begin'].includes(data.head.code)) {

                store[data.head.uuid].begin_time = data.head.time;

            } else if (['task:end', 'task:error'].includes(data.head.code)) {

                store[data.head.uuid].end_time = data.head.time;

                console.log(`[${data.head.uuid}]`, 'queued -> end', (
                    store[data.head.uuid].end_time - store[data.head.uuid].queued_time
                ), 'seconds');

                console.log(`[${data.head.uuid}]`, 'begin -> end', (
                    store[data.head.uuid].end_time - store[data.head.uuid].begin_time
                ), 'seconds');

                console.log(`[${data.head.uuid}]`, 'queued -> begin', (
                    store[data.head.uuid].begin_time - store[data.head.uuid].queued_time
                ), 'seconds');

            }

            // console.log(JSON.stringify(store))

        });

        document.getElementById('xml_merge_task_button').addEventListener("click", () => {
            websocket.send(JSON.stringify({
                head: {
                    code: 'task:exec',
                    uuid: ulid(),
                    time: `${new Date().getTime()}`
                },
                body: {
                    method: 'xml_merge',
                    params: {}
                },
            }));
        });

        document.getElementById('check_pdf_task_button').addEventListener("click", () => {
            websocket.send(JSON.stringify({
                head: {
                    code: 'task:exec',
                    uuid: ulid(),
                    time: `${new Date().getTime()}`
                },
                body: {
                    method: 'check_pdf',
                    params: {
                        contributions: generate_contributions()
                    }
                },
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

    });


});

console.log('start');


function generate_contributions() {

    const list = []

    for (let i = 1; i <= 1000; i++) {
        list.push({
            "code": "WEP60",
            "friendly_id": i,
            "id": 200 + i,
            "revisions": [
                {
                    "comment": "Thank you very much for the comments and the changes to the manuscript. We accept all the changes.",
                    "created_dt": "2022-08-22T09:32:45.386458+00:00",
                    "files": [
                        {
                            "content_type": "application/pdf",
                            "contribution_id": 200 + i,
                            "download_url": "http://127.0.0.1:8005/event/12/contributions/2591/editing/paper/5951/16667/WEP60.pdf",
                            "event_id": 12,
                            "filename": "WEP60.pdf",
                            "id": 1000 + i,
                            "revision_id": 1,
                            "uuid": "566123f7-bf12-44c5-a709-9ad50aaf2795"
                        }
                    ],
                    "id": 5951
                }
            ],
            "title": "Millimeter-Wave Undulators for Compact X-Ray Free-Electron Lasers"
        })
    }

    return list;

}



function ULID() {
    const BASE32 = [
        '0', '1', '2', '3', '4', '5', '6', '7',
        '8', '9', 'A', 'B', 'C', 'D', 'E', 'F',
        'G', 'H', 'J', 'K', 'M', 'N', 'P', 'Q',
        'R', 'S', 'T', 'V', 'W', 'X', 'Y', 'Z'
    ];
    let last = -1;
    /* Pre-allocate work buffers / views */
    let ulid = new Uint8Array(16);
    let time = new DataView(ulid.buffer, 0, 6);
    let rand = new Uint8Array(ulid.buffer, 6, 10);
    let dest = new Array(26);

    function encode(ulid) {
        dest[0] = BASE32[ulid[0] >> 5];
        dest[1] = BASE32[(ulid[0] >> 0) & 0x1f];
        for (let i = 0; i < 3; i++) {
            dest[i * 8 + 2] = BASE32[ulid[i * 5 + 1] >> 3];
            dest[i * 8 + 3] = BASE32[(ulid[i * 5 + 1] << 2 | ulid[i * 5 + 2] >> 6) & 0x1f];
            dest[i * 8 + 4] = BASE32[(ulid[i * 5 + 2] >> 1) & 0x1f];
            dest[i * 8 + 5] = BASE32[(ulid[i * 5 + 2] << 4 | ulid[i * 5 + 3] >> 4) & 0x1f];
            dest[i * 8 + 6] = BASE32[(ulid[i * 5 + 3] << 1 | ulid[i * 5 + 4] >> 7) & 0x1f];
            dest[i * 8 + 7] = BASE32[(ulid[i * 5 + 4] >> 2) & 0x1f];
            dest[i * 8 + 8] = BASE32[(ulid[i * 5 + 4] << 3 | ulid[i * 5 + 5] >> 5) & 0x1f];
            dest[i * 8 + 9] = BASE32[(ulid[i * 5 + 5] >> 0) & 0x1f];
        }
        return dest.join('');
    }

    return function () {
        let now = Date.now();
        if (now === last) {
            /* 80-bit overflow is so incredibly unlikely that it's not
             * considered as a possiblity here.
             */
            for (let i = 9; i >= 0; i--)
                if (rand[i]++ < 255)
                    break;
        } else {
            last = now;
            time.setUint16(0, (now / 4294967296.0) | 0);
            time.setUint32(2, now | 0);
            window.crypto.getRandomValues(rand);
        }
        return encode(ulid);
    };
}