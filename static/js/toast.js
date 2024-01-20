document.addEventListener('alpine:init', () => {
    Alpine.store('toasts', {
        counter: 0,
        list: [],
        createToast(message, type = 'info', timer = 2000) {
            const index = this.list.length
            let totalVisible =
                this.list.filter((toast) => {
                    return toast.visible
                }).length + 1
            this.list.push({
                id: this.counter++,
                message,
                type,
                timeOut: timer * totalVisible,
                visible: true,
            })
            setTimeout(() => {
                this.destroyToast(index)
            }, timer * totalVisible)
        },
        destroyToast(index) {
            this.list[index].visible = false
        },
    })
})