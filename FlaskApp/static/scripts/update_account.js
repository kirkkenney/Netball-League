var fileBtn = document.getElementById('picture')
var profileImg = document.getElementById('profileImg');

function showPreview() {
profileImg.src = window.URL.createObjectURL(this.files[0])
}

fileBtn.addEventListener('change', showPreview)

