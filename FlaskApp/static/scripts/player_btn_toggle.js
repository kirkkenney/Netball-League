var button = document.getElementsByClassName('js-toggle')

for (i = 0; i < button.length; i++)
{
    button[i].addEventListener("click", function()
    {
        if (this.classList.contains('btn-outline-primary'))
        {
            this.classList.remove('btn-outline-primary');
            this.classList.add('btn-success');
        } else {
            this.classList.remove('btn-success');
            this.classList.add('btn-outline-primary');
        }
    })
}
