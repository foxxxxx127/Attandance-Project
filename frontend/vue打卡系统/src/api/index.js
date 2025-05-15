import request from '@/utils/request.js'

export const loginService = (logindata)=>{
    const params = new URLSearchParams()
    for(let key in logindata){
        params.append(key,logindata[key]);
    }
    return request.post('/login',params)
}
export const cardApplicationService=(cardApplicationData)=>{
    const params = new URLSearchParams()
    for(let key in cardApplicationData){
        params.append(key,cardApplicationData[key]);
    }
    return request.post('/cardapplication',params)
}