import { defineStore } from "pinia";

export const useUserInfo = defineStore('userInfo', {
    state: () => ({
        userId: 123424,
       
    }),
    persist: true // 启用持久化
})

