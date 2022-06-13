const axios=require('axios');

async function post(){
    let res = await  axios({
        url: 'https://backend.ethmore.pro/api/v1/setNftData', // 向url发送请求
        method: 'post', // 指定psot请求
        data:{'tokenId': 0, 'minter': '3423412dfasf','owner':'123adfs','collection':'asdfasdfasd','txhash':'asdfasdfasd'}, // 携带数据
    })
    console.log(res.data) // 后端传回的数据
}

post();
