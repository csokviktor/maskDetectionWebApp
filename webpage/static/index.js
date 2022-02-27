function deleteNote(noteID){
    fetch('/delete-note', {
        method: 'POST',
        body: JSON.stringify({noteID: noteID})
    }).then((_res) => {window.location.href = '/';});
}

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