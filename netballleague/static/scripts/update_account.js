window.onload = function() {

    if (document.getElementById('picture')) {

        var fileBtn = document.getElementById('picture')
        var profileImg = document.getElementById('profileImg');

        function showPreview() {
        profileImg.style.background = 'url(' + window.URL.createObjectURL(this.files[0]) + ')';
        profileImg.style.backgroundSize = 'contain';
        profileImg.style.backgroundPosition = 'center';
        }

        fileBtn.addEventListener('change', showPreview)
    }
}
