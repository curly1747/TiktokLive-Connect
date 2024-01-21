$(document).ready(function () {

    const socket = io();

    socket.on("connect", () => {
        socket.emit('queue', '');
    });

    socket.on("queue", (data) => {
        data.length ? check_queue(data) : $("#queue").html("")
    });

    socket.on("speed", (data) => {
        check_speed(data)
    });

    let pause_state = false
    socket.on("pause_state", (r) => {
        pause_state = r
    });

    function render_queue(event, is_set_playing) {
        let is_playing = false
        if (!is_set_playing) {
            if (!pause_state) {
                is_playing = true
            }
        }
        return `
            <div class="bg-slate-800 hover:bg-slate-700 shadow rounded-2xl p-5 cursor-pointer gift-item basis-1/2">
                <div class="flex items-center gap-6 ">
                    <img src="${event.ava}"
                         alt="" class="h-16 rounded-full ${is_playing ? "animate-spin" : ""}">
                    <div class="w-full flex flex-row items-center align-center gap-4 text-slate-300 justify-between text-xl">
                        <h2 class="mb-1 w-2/2 truncate">
                            ${is_playing ? '<iconify-icon class="text-xl ltr:mr-2 rtl:ml-2" icon="svg-spinners:bars-scale-middle"></iconify-icon>' : ""}
                            ${event.user}
                        </h2>
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
        let is_set_playing = false
        $.each(data, function (i, event) {
            if ((event.id === last_event.id) && (event.user === last_event.user)) {
                last_event.count += 1
            } else {
                if (last_event.count) {
                    html += render_queue(last_event, is_set_playing)
                    is_set_playing = true
                }
                last_event = event
                last_event.count = 1
            }
        });
        html += render_queue(last_event, is_set_playing)
        $('#queue').html(html)
    }

    function render_speed(event, is_set_speeding) {
        if (event.types.includes('FAST')) {
            return `
                <span class="badge bg-success-500 text-success-500 bg-opacity-30 capitalize font-bold">${is_set_speeding ? "": "Đang "} Tăng Tốc x${event.count}</span>
            `
        } else if (event.types.includes('SLOW')) {
            return `
                <span class="badge bg-danger-500 text-danger-500 bg-opacity-30 capitalize font-bold">${is_set_speeding ? "": "Đang "} Giảm Tốc x${event.count}</span>
            `
        }
    }

    function check_speed(data) {
        let html = `
            
        `
        let is_set_speeding = false
        let last_event = {'id': false, 'count': 0}
        $.each(data, function (i, event) {
            html += function render_speed(event, is_set_speeding) {
        if (event.types.includes('FAST')) {
            return `
                <span class="badge bg-success-500 text-success-500 bg-opacity-30 capitalize font-bold">${is_set_speeding ? "": "Đang "} Tăng Tốc x${event.count}</span>
            `
        } else if (event.types.includes('SLOW')) {
            return `
                <span class="badge bg-danger-500 text-danger-500 bg-opacity-30 capitalize font-bold">${is_set_speeding ? "": "Đang "} Giảm Tốc x${event.count}</span>
            `
        }
    }(event, is_set_speeding)
            is_set_speeding = true
        });
        $('#speed').html(html)
    }
});