$(document).ready(function () {

    const socket = io();

    socket.on("connect", () => {
        socket.emit('queue', '');
    });

    socket.on("queue", (data) => {
        data.length ? check_queue(data) : ''
    });

    socket.on("speed", (data) => {
        check_speed(data)
    });

    function render_queue(event) {
        return `
            <div class="bg-slate-800 hover:bg-slate-700 shadow rounded-2xl p-5 cursor-pointer gift-item w-full">
                <div class="flex items-center gap-6 ">
                    <img src="${event.ava}"
                         alt="" class="h-16 rounded-full">
                    <div class="w-full flex flex-row items-center align-center gap-4 text-slate-300 justify-between text-xl">
                        <h2 class="mb-1 w-2/2 truncate">${event.user}</h2>
                        <div class="flex items-center align-center gap-2 w-1/3 justify-end">
                            <img src="${event.thumbnail}"
                                 alt="" class="h-12 rounded-full">
                            <span class="font-bold w-10">x${event.count}</span>
                        </div>
                    </div>
                </div>
            </div>
        `
    }

    function check_queue(data) {
        let html = `
            <div class="flex flex-col w-full gap-2">
                <div class="flex justify-between text-slate-300 text-base font-bold px-2">
                    <span>Danh sách phát</span>
                    <span>(${data.length})</span>
                </div>
                <div id="speed" class="flex flex-wrap gap-2 px-2"></div>
            </div>
            
        `
        let last_event = {'id': false, 'user': false, 'count': 0}
        $.each(data, function (i, event) {
            if ((event.id === last_event.id) && (event.user === last_event.user)) {
                last_event.count += 1
            } else {
                if (last_event.count) {
                    html += render_queue(last_event)
                }
                last_event = event
                last_event.count = 1
            }
        });
        html += render_queue(last_event)
        $('#queue').html(html)
    }

    function render_speed(event) {
        if (event.types.includes('FAST')) {
            return `
                <span class="badge bg-success-500 text-success-500 bg-opacity-30 capitalize font-bold">Tăng Tốc x${event.count}</span>
            `
        } else if (event.types.includes('SLOW')) {
            return `
                <span class="badge bg-danger-500 text-danger-500 bg-opacity-30 capitalize font-bold">Giảm Tốc x${event.count}</span>
            `
        }
    }

    function check_speed(data) {
        let html = `
            
        `
        let last_event = {'id': false, 'count': 0}
        $.each(data, function (i, event) {
            if ((event.id === last_event.id)) {
                last_event.count += 1
            } else {
                if (last_event.count) {
                    html += render_speed(last_event)
                }
                last_event = event
                last_event.count = 1
            }
        });
        html += render_speed(last_event)
        $('#speed').html(html)
    }
});