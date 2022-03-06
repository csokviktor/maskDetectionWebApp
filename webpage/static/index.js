function deleteUser(userID){
    fetch('/delete-user', {
        method: 'POST',
        body: JSON.stringify({userID: userID})
    }).then((_res) => {window.location.href = '/edit-user';});
}

function updateAdminRights(userID){
    fetch('/update-user', {
        method: 'POST',
        body: JSON.stringify({userID: userID})
    }).then((_res) => {window.location.href = '/edit-user';});
}

function deleteCamera(cameraID){
    fetch('/delete-camera', {
        method: 'POST',
        body: JSON.stringify({cameraID: cameraID})
    }).then((_res) => {window.location.href = '/camera-management';});
}