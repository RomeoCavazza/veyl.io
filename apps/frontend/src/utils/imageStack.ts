// Image Stack Utility - For cascade effect from portfolio/pages/social-platform.html

export function toggleProjectImages(container: HTMLElement) {
  const images = container.querySelectorAll<HTMLElement>('.stack-image');
  
  // Retirer toutes les classes
  images.forEach(img => {
    img.classList.remove('active', 'hidden', 'back');
  });
  
  // Trouver l'index de l'image active
  let currentImageIndex = -1;
  images.forEach((img, index) => {
    if (img.classList.contains('active')) {
      currentImageIndex = index;
    }
  });
  
  // Si aucune active, commencer à 0
  if (currentImageIndex === -1) {
    currentImageIndex = 0;
  }
  
  // Passer à l'image suivante
  const nextIndex = (currentImageIndex + 1) % images.length;
  
  // Appliquer les états avec dégradé
  images.forEach((img, index) => {
    if (index === nextIndex) {
      img.classList.add('active');
    } else if (index === (nextIndex + 1) % images.length) {
      img.classList.add('hidden');
    } else {
      img.classList.add('back');
    }
  });
}

export function initImageStack(container: HTMLElement) {
  const images = container.querySelectorAll<HTMLElement>('.stack-image');
  images.forEach((img, index) => {
    if (index === 0) {
      img.classList.add('active');
    } else if (index === 1) {
      img.classList.add('hidden');
    } else {
      img.classList.add('back');
    }
  });
}

