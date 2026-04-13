<script>
  document.addEventListener('DOMContentLoaded', function () {
    const menuLateral = document.getElementById('menuLateral');
  const bsOffcanvas = new bootstrap.Offcanvas(menuLateral);
  const links = menuLateral.querySelectorAll('.nav-link');

    links.forEach(link => {
    link.addEventListener('click', () => {
      // Verifica se o menu está aberto antes de tentar esconder
      if (menuLateral.classList.contains('show')) {
        bsOffcanvas.hide();
      }
    });
    });
  });

</script>