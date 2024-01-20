$(document).ready(function () {

    const socket = io();

    const pk = $('#pk');

    let is_hide_pk = true;

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

    const bar_a = $('#bar_a')
    const bar_b = $('#bar_b')

    function bar_state(e, state) {
        if (state) {
            e.removeClass('stop_animation')
        } else {
            e.addClass('stop_animation')
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


    socket.on("update_pk", (data) => {
        update_data(data)
    });

    socket.on("connect", () => {
        setInterval(function () {
            socket.emit('update_remain_time', '');
        }, 3 * 1000)
    });

    const remain_time_label = $("#remain_time_label")
    socket.on("update_remain_time", (data) => {
        remain_time.text(data)
        if (data === "Kết Thúc") {
            if (!is_hide_pk){
                setTimeout(function (){
                    if (is_hide_pk){
                        pk.addClass('hidden')
                    }
                }, 60*1000)
                is_hide_pk = true
            }
            remain_time_label.addClass('hidden')
        } else {
            hide_status()
            is_hide_pk = false
            pk.removeClass('hidden')
            remain_time_label.removeClass('hidden')
        }
    });

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

    function hide_status() {
        $.each(['a', 'b'], function (i, team) {
            let team_e = $("#name_" + team)
            team_e.find('.win').addClass('hidden')
            team_e.find('.lose').addClass('hidden')
            team_e.find('.raw').addClass('hidden')
        })
    }

    socket.on("start_pk", (r) => {
        if (r.success) {
            pk.removeClass('hidden')
            remain_time.text(r.msg)
            new_pk()
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
    });

});