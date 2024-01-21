$(document).ready(function () {

    const socket = io();

    setInterval(function () {
        count_down()
    }, 1000)
    const remain_time = $("#remain_time")

    function count_down() {
        let t = remain_time.text()
        if ((t !== "Kết Thúc") && (t !== "") && (t !== "0")) {
            remain_time_label.removeClass('hidden')
            if (t) {
                t = +t
                remain_time.text(t - 1)
            }
        }
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

    function render_loading(type = 'loading') {
        const render = {
            'loading': `
                <iconify-icon class="text-xl spin-slow ltr:mr-2 rtl:ml-2 relative top-[1px]" icon="line-md:loading-twotone-loop"></iconify-icon>
                <span>Đang Gửi</span>
            `,
            'success': `
                <iconify-icon class="text-xl spin-slow ltr:mr-2 rtl:ml-2 relative top-[1px]" icon="line-md:check-all"></iconify-icon>
                <span>Thành công</span>
            `,
            'error': `
                <span>Thử lại</span>
            `
        }
        return render[type]

    }

    $('#connect').click(function () {
        $(this).find('.flex').find('span').html('Đang kết nối...')
        $(this).prop('disabled', true)
        $('#start').prop('disabled', false)
        socket.emit('tiktok_client_connect', '');
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


    const bar_a = $('#bar_a')
    const bar_b = $('#bar_b')

    function bar_state(e, state) {
        if (state) {
            e.removeClass('stop_animation')
        } else {
            e.addClass('stop_animation')
        }
    }

    function update_bar_state() {
        let current_a = bar_a.width()
        let current_b = bar_b.width()

        if (current_a < current_b / 2) {
            bar_state(bar_a, false)
            bar_state(bar_b, true)
        } else if (current_a === current_b / 2) {
            bar_state(bar_a, true)
            bar_state(bar_b, true)
        } else {
            bar_state(bar_a, true)
            bar_state(bar_b, false)
        }
    }

    function update_point(e, width, point) {
        const speed = 300
        const bar_width = $("#bar").width()
        e.width(width * bar_width)
        const point_e = $(e.data('point'))
        if (+point_e.text() !== point) {
            setTimeout(function () {
                point_e.text(point)
            }, speed / 2)
            point_e.stop(true, true).animate({zoom: '150%'}, speed / 2).animate({zoom: '100%'}, speed / 2);
        }
    }

    update_data([$("#bar_a").data("init-point"), $("#bar_b").data("init-point")])

    function update_data(data) {
        const point_a = +data[0]
        const point_b = +data[1]
        const total = point_a + point_b
        const percent_a = point_a / total
        const percent_b = point_b / total
        update_point(bar_a, percent_a, point_a)
        update_point(bar_b, percent_b, point_b)
    }

    $('#test').click(function () {
        let data = [Math.floor(1 + Math.random() * 9999), Math.floor(1 + Math.random() * 9999)]
        update_data(data)
    })

    $.each($('.data-gift'), function (index, e) {
        let ts = new TomSelect(e, {
            allowEmptyOption: true,
            maxItems: 5,
            render: {
                option: function (data, escape) {
                    const label = data.text.split('|');
                    if (label.length === 2) {
                        return `
                            <div class="flex items-center">
                              <div class="flex-none">
                                <div class="w-8 h-8 ltr:mr-3 rtl:ml-3">
                                  <img src="${data.src}" alt="" class="w-full h-full object-cover">
                                </div>
                              </div>
                              <div class="flex-1 flex-row text-start">
                                <h4 class="text-sm font-medium text-slate-600 whitespace-nowrap">
                                  ${label[0]}
                                </h4>
                                <div class="flex">
                                    <div class="w-4 h-4 mr-1">
                                        <img src="/static/images/coin.png" alt="" class="w-full h-full object-cover">
                                    </div>
                                    <div class="text-xs font-normal text-slate-600 dark:text-slate-400">
                                      ${label[1]}
                                    </div>
                                </div>
                              </div>
                            </div>
                    `;
                    } else {
                        return `
                            <div class="flex items-center hidden">
                              <div class="flex-none">
                                <div class="w-8 h-8 ltr:mr-3 rtl:ml-3">
                                  
                                </div>
                              </div>
                              <div class="flex-1 flex-row text-start">
                                <h4 class="text-sm font-medium text-slate-600 whitespace-nowrap">
                                  ${label[0]}
                                </h4>
                                <div class="flex">
                                    <div class="w-4 h-4 mr-1">
                                        
                                    </div>
                                    <div class="text-xs font-normal text-slate-600 dark:text-slate-400">
                                    </div>
                                </div>
                              </div>
                            </div>
                    `;
                    }
                },
                item: function (data, escape) {
                    const label = data.text.split('|')
                    if (label.length === 2) {
                        return `
                            <div class="flex items-center">
                              <div class="flex-none">
                                <div class="w-8 h-8 ltr:mr-3 rtl:ml-3">
                                  <img src="${data.src}" alt="" class="w-full h-full object-cover">
                                </div>
                              </div>
                              <div class="flex-1 flex-row text-start">
                                <h4 class="text-sm font-medium text-slate-600 whitespace-nowrap">
                                  ${label[0]}
                                </h4>
                                <div class="flex">
                                    <div class="w-4 h-4 mr-1">
                                        <img src="/static/images/coin.png" alt="" class="w-full h-full object-cover">
                                    </div>
                                    <div class="text-xs font-normal text-slate-600 dark:text-slate-400">
                                      ${label[1]}
                                    </div>
                                </div>
                              </div>
                            </div>
                    `;
                    } else {
                        return `
                            <div class="flex items-center">
                              <div class="flex-none">
                                <div class="w-8 h-8 ltr:mr-3 rtl:ml-3">
                                  
                                </div>
                              </div>
                              <div class="flex-1 flex-row text-start">
                                <h4 class="text-sm font-medium text-slate-600 whitespace-nowrap">
                                  ${label[0]}
                                </h4>
                                <div class="flex">
                                    <div class="w-4 h-4 mr-1">
                                        
                                    </div>
                                    <div class="text-xs font-normal text-slate-600 dark:text-slate-400">
                                    </div>
                                </div>
                              </div>
                            </div>
                    `;
                    }

                }
            }
        });
        ts.clear()
    });

    $("#config_button").click(function () {
        $.each(modal_config.find('select'), function (i, e) {
            e.tomselect.setValue($(e).data('json'))
        })
    })

    const modal_config = $("#config")
    modal_config.find('button.submit').click(function () {
        $(this).html(render_loading())
        $(this).prop('disabled', true)
        let data = {
            'duration': +modal_config.find('.duration').val(),
            'name': modal_config.find('.round_name').val(),
            'a': {
                'name': modal_config.find('.name_a').val(),
                'gifts': modal_config.find('#gifts_a').val().map(function (e) {
                    return +e
                }),
            },
            'b': {
                'name': modal_config.find('.name_b').val(),
                'gifts': modal_config.find('#gifts_b').val().map(function (e) {
                    return +e
                }),
            }
        }
        socket.emit('pk_config', data);
    })

    socket.on("pk_config", (r) => {
        const button = modal_config.find("button.submit")
        socket_verify(r, button)
    });

    socket.on("update_pk", (data) => {
        update_data(data)
    });

    socket.on("connect", () => {
        setInterval(function () {
            socket.emit('update_remain_time', '');
        }, 5 * 1000)
    });

    const remain_time_label = $("#remain_time_label")
    socket.on("update_remain_time", (data) => {
        remain_time.text(data)
        if (data === "Kết Thúc") {
            remain_time_label.addClass('hidden')
        } else {
            remain_time_label.removeClass('hidden')
        }
    });

    $("#start").click(function () {
        $(this).prop('disabled', true)
        $(this).toggleClass('btn-primary btn-success')
        socket.emit('start_pk', '');
    })

    function new_pk() {
        $.each(['a', 'b'], function (i, team) {
            let team_e = $("#name_" + team)
            team_e.find('.win').addClass('hidden')
            team_e.find('.lose').addClass('hidden')
            team_e.find('.raw').addClass('hidden')
            remain_time_label.removeClass('hidden')
            $("#point_" + team).text("0")
            $("#bar_" + team).width("50%")
        })
    }

    socket.on("start_pk", (r) => {
        const button = $("#start")
        if (r.success) {
            button.find('span').text('Đang PK')
            remain_time.text(r.msg)
            new_pk()
        } else {
            button.find('span').text('Bắt Đầu')
            button.prop('disabled', false)
            Alpine.store('toasts').createToast(r.msg, 'error');
        }
    });

    socket.on("stop_pk", (data) => {
        let team_win = ''
        let team_lose = ''
        if (data[0] > data[1]) {
            team_win = 'a'
            team_lose = 'b'
        } else if (data[0] < data[1]) {
            team_win = 'b'
            team_lose = 'a'
        } else {
            team_win = '0'
            team_lose = '0'
        }

        if (team_win !== team_lose) {
            let team_win_e = $("#name_" + team_win)
            let team_lose_e = $("#name_" + team_lose)
            team_win_e.find('.win').removeClass('hidden')
            team_lose_e.find('.lose').removeClass('hidden')
        } else {
            $("#name_a").find('.raw').removeClass('hidden')
            $("#name_b").find('.raw').removeClass('hidden')
        }

        let start_btn = $("#start")
        start_btn.prop('disabled', false)
        start_btn.find('span').text('Bắt đầu')
        start_btn.toggleClass('btn-primary btn-success')
    });

    function render_sound_input(val = '') {
        return `
            <div class="flex items-center">
                <input type="text" name="gift_sound[]" class="form-control pb-2" placeholder="Nhập đường dẫn file nhạc (trên máy)" value="${val}">
                <div class="remove_sound ml-2">
                    <iconify-icon class="text-xl" icon="ph:minus-fill"></iconify-icon>
                </div>
            </div>
        `
    }


    const modal_music_config = $("#music_config")

    $('.sound_group .sg_header').on("click", function () {
        const e = render_sound_input()
        $('.sound_group .sg_body').append(e)
        $('.remove_sound').on("click", function () {
            $(this).parent().remove()
        })
    })

    let sounds = modal_music_config.data('sounds')

    if (sounds.constructor !== Array){
        sounds = JSON.parse(sounds.replaceAll("'", '"'))
    }
    console.log(sounds)
    if (sounds.length) {
        modal_music_config.find('.sound_group .sg_body').html("")
        $.each(sounds, function (index, path) {
            const e = render_sound_input(path)
            modal_music_config.find('.sound_group .sg_body').append(e)
            $('.remove_sound').on("click", function () {
            $(this).parent().remove()
        })
        });
    }


    modal_music_config.find('button.submit').click(function () {
        $(this).html(render_loading())
        $(this).prop('disabled', true)
        let sounds = $('input[name="gift_sound[]"]').map(function () {
            return $(this).val()
        }).get();
        const data = {
            'sounds': sounds,
        }
        socket.emit('update_pk_music', data);
    })

    socket.on("update_pk_music", (r) => {
        const button = modal_music_config.find("button.submit")
        socket_verify(r, button)
    });
});