$(document).ready(function () {

    const socket = io();


    socket.on("connect", () => {
        socket.emit('queue', '');
    });

    function render_loading(type = 'loading', text='Đang gửi') {
        const render = {
            'loading': `
                <iconify-icon class="text-xl spin-slow ltr:mr-2 rtl:ml-2 relative top-[1px]" icon="line-md:loading-twotone-loop"></iconify-icon>
                <span>${text}</span>
            `,
            'success': `
                <iconify-icon class="text-xl spin-slow ltr:mr-2 rtl:ml-2 relative top-[1px]" icon="line-md:check-all"></iconify-icon>
                <span>Thành công</span>
            `,
            'error': `
                <span>Thử lại</span>
            `,
            'text': `
                <span>${text}</span>
            `
        }
        return render[type]

    }

    function socket_verify(r, button) {
        if (r.success) {
            button.html(render_loading('success'))
            if (r.location) {
                location.replace(r.location)
            } else {
                location.reload()
            }

        } else {
            button.html(render_loading('error'))
            button.prop('disabled', false)
            Alpine.store('toasts').createToast(r.msg, 'error');
        }
    }

    socket.on("update_app_setting", (r) => {
        const button = modal_app_setting.find("button.submit")
        socket_verify(r, button)
    });

    socket.on("pause", (r) => {
        $('#pause').data('state', r.msg)
    });

    socket.on("queue", (data) => {
        data.length ? check_queue(data) : ''
    });

    socket.on("speed", (data) => {
        check_speed(data)
    });


    socket.on("tiktok_client_connect", (r) => {
        const button = $('#connect')
        if (r.success) {
            button.find('.flex').find('span').html(r.msg)
            button.addClass('btn-success')
            button.removeClass('btn-danger')
        } else {
            button.find('.flex').find('span').html("Kết nối")
            button.prop('disabled', false)
            Alpine.store('toasts').createToast(r.msg, 'error');
        }
    });

    function render_queue(event) {
        return `
            <div class="bg-slate-800 hover:bg-slate-700 shadow rounded-2xl p-5 cursor-pointer gift-item basis-1/2">
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
            <div class="flex flex-col basis-1/2 gap-2">
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
        if (event.types.includes('FAST')){
            return `
                <span class="badge bg-success-500 text-success-500 bg-opacity-30 capitalize font-bold">Tăng Tốc x${event.count}</span>
            `
        } else if (event.types.includes('SLOW')){
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

    const modal_app_setting = $("div#app_setting")
    modal_app_setting.find("button.submit").click(function () {
        $(this).html(render_loading())
        $(this).prop('disabled', true)

        let types = $('input[name="queue_type[]"]:checked').map(function () {
            return $(this).val()
        }).get();

        const data = {
            'room_id': modal_app_setting.find('input.room_id').val(),
            'play_delay': modal_app_setting.find('input.play_delay').val(),
            'queue_type': types[0]
        }
        socket.emit('update_app_setting', data);
    });

    $('#connect').click(function () {
        $(this).find('.flex').find('span').html('Đang kết nối...')
        $(this).prop('disabled', true)
        $('#pause').prop('disabled', false)
        socket.emit('tiktok_client_connect', '');
    });

    $('#pause').click(function () {
        $(this).find('.pause').toggleClass('hidden')
        $(this).find('.resume').toggleClass('hidden')

        const state_map = {
            'True': true,
            'False': false,
            'true': true,
            'false': false
        }

        let data = {
            'state': state_map[$(this).data('state')]
        }
        socket.emit('pause', data);
    });

    $('#add_music button.submit').click(function () {
        const form = $(this).parent()
        const data = {
            'gift': form.data('id'),
            'quantity': parseInt(form.find('input').val()),
        }
        socket.emit('add_queue', data);
    });

});