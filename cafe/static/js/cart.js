var updateBtns = document.getElementsByClassName('update-cart')
console.log('Hello world')
for (i = 0; i < updateBtns.length; i++) {
    updateBtns[i].addEventListener('click', function(){
        var productId = this.dataset.product
        var action = this.dataset.action
        console.log('productId:', productId, 'Action:', action)
        console.log('USER:', user)
        if(user == 'AnonymousUser'){
            console.log('Not logged in')
        }else{
            console.log('Synced')
            updateUserOder(productId, action)
        }
    })
}

//function updateUserOder(productId, action){
//    console.log('All is fine')
//    var url = '/update_item/'
//    fetch(url, {
//        method: 'POST',
//        headers: {'Content-Type': 'application/json',
//                'X-CSRFtoken': csrftoken,
//        },
//        body:JSON.stringify({'productId': productId, 'action': action})
//        })
//        .then((response) =>{
//            return response.json()
//        })
//        .then((data) =>{
//            console.log("Data:", data)
//        });
//}