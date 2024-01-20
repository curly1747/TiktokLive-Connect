$(document).ready(function () {

    const socket = io();

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

    socket.on("create_profile", (r) => {
        const button = modal_add_profile.find("button.submit")
        socket_verify(r, button)
    });

    socket.on("add_gift", (r) => {
        const button = modal_add_gift.find("button.submit")
        socket_verify(r, button)
    });

    socket.on("edit_gift", (r) => {
        const button = modal_edit_gift.find("button.submit")
        socket_verify(r, button)
    });

    socket.on("delete_gift", (r) => {
        const button = modal_edit_gift.find("button.delete")
        socket_verify(r, button)
    });

    socket.on("delete_profile", (r) => {
        const button = modal_delete_profile.find("button.submit")
        socket_verify(r, button)
    });

    socket.on("update_profile_setting", (r) => {
        const button = modal_profile_setting.find("button.submit")
        socket_verify(r, button)
    });

    socket.on("set_default_profile", (r) => {
        const button = $('.set_default_profile')
        socket_verify(r, button)
    });


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

    const modal_add_profile = $("div#add_profile")
    modal_add_profile.find("button.submit").click(function () {
        $(this).html(render_loading())
        $(this).prop('disabled', true)
        socket.emit('create_profile', modal_add_profile.find('input.profile_name').val());
    });

    const modal_add_gift = $("div#add_gift")
    modal_add_gift.find("button.submit").click(function () {
        $(this).html(render_loading())
        $(this).prop('disabled', true)
        let types = $('input[name="gift_type[]"]:checked').map(function () {
            return $(this).val()
        }).get();
        let sounds = $('input[name="gift_sound[]"]').map(function () {
            return $(this).val()
        }).get();
        const data = {
            'profile': modal_add_gift.find('input.profile_name').val(),
            'id': modal_add_gift.find('.data-gift').val(),
            'name': modal_add_gift.find('input.gift_name').val(),
            'types': types,
            'sounds': sounds,
        }
        socket.emit('add_gift', data);
    });

    const modal_delete_profile = $("div#delete_profile")
    modal_delete_profile.find("button.submit").click(function () {
        $(this).html(render_loading())
        $(this).prop('disabled', true)
        socket.emit('delete_profile', $(this).data('profile'));
    });

    $('.set_default_profile').on("click", function () {
        socket.emit('set_default_profile', $(this).data('profile'));
    })

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

    $('.sound_group .sg_header').on("click", function () {
        const e = render_sound_input()
        $('.sound_group .sg_body').append(e)
        $('.remove_sound').on("click", function () {
            $(this).parent().remove()
        })
    })

    const modal_profile_setting = $("div#profile_setting")
    modal_profile_setting.find("button.submit").click(function () {
        $(this).html(render_loading())
        $(this).prop('disabled', true)

        const data = {
            'profile': modal_profile_setting.find('input.profile_name').val(),
            'background_music': modal_profile_setting.find('input.background_music').val(),
            'cross_music': modal_profile_setting.find('input.cross_music').val()
        }
        socket.emit('update_profile_setting', data);
    });

    const modal_edit_gift = $("div#edit_gift")

    function clear_edit_gift_form() {
        modal_edit_gift.find('.data-gift').get(0).tomselect.setValue(0)
        modal_edit_gift.find('input.gift_name').val('')
        modal_edit_gift.find('.sound_group .sg_body').html('')
        $.each(modal_edit_gift.find('input[name="gift_type[]"]'), function (index, type) {
            $(type).prop('checked', false);
        });
    }

    $('.gift-item').on("click", function () {
        clear_edit_gift_form()
        const data = JSON.parse($(this).data('json').replaceAll("'", '"'))
        modal_edit_gift.find('.data-gift').get(0).tomselect.setValue(data.id)
        modal_edit_gift.find('input.gift_name').val(data.name)
        $.each(data.sounds, function (index, path) {
            const e = render_sound_input(path)
            modal_edit_gift.find('.sound_group .sg_body').append(e)
        });

        $.each(data.types, function (index, type) {
            modal_edit_gift.find(`input[value="${type}"]`).prop('checked', true);
        });
    })

    modal_edit_gift.find("button.submit").click(function () {
        $(this).html(render_loading())
        $(this).prop('disabled', true)
        let types = $('input[name="gift_type[]"]:checked').map(function () {
            return $(this).val()
        }).get();
        let sounds = $('input[name="gift_sound[]"]').map(function () {
            return $(this).val()
        }).get();
        const data = {
            'profile': modal_edit_gift.find('input.profile_name').val(),
            'id': modal_edit_gift.find('.data-gift').val(),
            'name': modal_edit_gift.find('input.gift_name').val(),
            'types': types,
            'sounds': sounds,
        }
        socket.emit('edit_gift', data);
    });

    modal_edit_gift.find("button.delete").click(function () {
        $(this).html(render_loading())
        $(this).prop('disabled', true)
        const data = {
            'profile': modal_edit_gift.find('input.profile_name').val(),
            'id': modal_edit_gift.find('.data-gift').val(),
        }
        socket.emit('delete_gift', data);
    });

    $('.remove_sound').on("click", function () {
        $(this).parent().remove()
    })

    $('button.add_gift').on('click', function () {
        const profile = $(this).data('profile');
        $('#add_gift input.profile_name').val(profile);
    })

    $.each($('.data-gift'), function (index, e) {
        new TomSelect(e, {
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
    });
});