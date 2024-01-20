$(document).ready(function () {

    const socket = io();

    socket.on("create_profile", (r) => {
        if (r.success) {
            location.replace('/profile/' + r.msg);
        } else {
            Alpine.store('toasts').createToast(r.msg, 'error');
        }

    });

    const modal_add_profile = $("div#add_profile")
    modal_add_profile.find("button").click(function () {
        socket.emit('create_profile', modal_add_profile.find('input.profile_name').val());
    });
});