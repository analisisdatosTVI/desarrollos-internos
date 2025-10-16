// This function delays executing a function (func) until after a certain
// time (delay) has passed without it being called again.
function debounce(func, delay = 500) {
  let timeout;
  return (...args) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => {
      func.apply(this, args);
    }, delay);
  };
}

document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('.filter-form');
    const calendarContainer = document.querySelector('.calendar-container');
    const spinner = document.getElementById('loading-spinner');

    if (form && calendarContainer && spinner) {
        form.addEventListener('submit', () => {
            calendarContainer.classList.add('loading');
            spinner.style.display = 'block';
        });
    }

    // --- AUTO-SUBMIT LOGIC ---
    const autoSubmit = () => {
      if (form) {
        form.submit();
      }
    };
    
    const debouncedSubmit = debounce(autoSubmit, 500); // 500ms delay

    const filterInputs = document.querySelectorAll(
      '#year, #apartament, input[name="fractions"]'
    );

    filterInputs.forEach(input => {
      input.addEventListener('change', debouncedSubmit);
    });

    // --- NEW: LOGIC TO UNCHECK "ALL" ---
    const allCheckbox = document.getElementById('fraction_all');
    const individualFractionCheckboxes = document.querySelectorAll(
        'input[name="fractions"]:not(#fraction_all)'
    );

    if (allCheckbox) {
        individualFractionCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', () => {
                // If the "All" box is checked and we have just unchecked an individual box...
                if (allCheckbox.checked && !checkbox.checked) {
                    // ...then uncheck the "All" box as well.
                    allCheckbox.checked = false;
                }
            });
        });
    }
});

function deselectAll() {
  const checkboxes = document.querySelectorAll('input[name="fractions"]');
  checkboxes.forEach(checkbox => checkbox.checked = false);
  document.querySelector('.filter-form').submit();
}

// This listener handles all other interactivity
window.addEventListener('DOMContentLoaded', () => {
  console.log("scripts.js loaded correctly");
  
  // --- Global Tooltip Setup ---
  let tooltip = document.createElement('div');
  tooltip.className = 'tooltip';
  document.body.appendChild(tooltip);

  const datesWithTooltips = document.querySelectorAll('[data-tooltip]');
  datesWithTooltips.forEach(el => {
    el.addEventListener('mouseenter', () => {
      const tooltipText = el.getAttribute('data-tooltip');
      if (tooltipText && tooltipText.trim() !== '' && tooltipText.trim() !== '-') {
        tooltip.textContent = tooltipText;
        tooltip.style.visibility = 'visible';
        tooltip.style.opacity = '1';
      }
    });

    el.addEventListener('mousemove', (e) => {
      tooltip.style.left = `${e.clientX + 15}px`;
      tooltip.style.top = `${e.clientY - 30}px`;
    });

    el.addEventListener('mouseleave', () => {
      tooltip.style.opacity = '0';
      tooltip.style.visibility = 'hidden';
    });
  });

  // --- Floating Error Message Handler ---
  const errorDiv = document.getElementById('floating-error');
  if (errorDiv) {
    const message = errorDiv.getAttribute('data-message');
    if (message) {
        errorDiv.textContent = message;
        setTimeout(() => {
            errorDiv.style.opacity = '0';
            setTimeout(() => errorDiv.remove(), 500);
        }, 3000);
    }
  }
  
  function updateMonthVisibility() {
    const checkedFractions = document.querySelectorAll('input[name="fractions"]:checked');
    if (checkedFractions.length !== 1) return;
    
    const selectedValue = checkedFractions[0].value;
    const allMonths = document.querySelectorAll('.month');

    allMonths.forEach(month => {
      let monthHasVisibleDay = false;
      for (const day of month.querySelectorAll('.date-circle')) {
        const tooltipText = day.getAttribute('data-tooltip') || '';
        
        if (selectedValue === 'unfractional') {
            if (tooltipText.includes('Unfractioned')) {
                monthHasVisibleDay = true;
                break;
            }
        } else {
            const fractionNumber = selectedValue === '0' ? '8' : selectedValue;
            if (tooltipText.includes(`Fraction ${fractionNumber}`)) {
                monthHasVisibleDay = true;
                break;
            }
        }
      }
      if (!monthHasVisibleDay) month.style.display = 'none';
    });
  }
  updateMonthVisibility();

  const fractionLabels = document.querySelectorAll('.fraction-label');
  const calendar = document.querySelector('.calendar');

  if (calendar) {
      fractionLabels.forEach(label => {
          label.addEventListener('mouseenter', () => {
              const fractionValue = label.dataset.fractionValue;
              if (fractionValue === 'all') return;

              calendar.classList.add('dimmed');
              calendar.querySelectorAll('.date-circle').forEach(day => {
                  const tooltipText = day.getAttribute('data-tooltip') || '';
                  if (fractionValue === 'unfractional') {
                      if (tooltipText.includes('Unfractioned')) {
                          day.classList.add('highlight');
                      }
                  } else {
                      const fractionNumber = fractionValue === '0' ? '8' : fractionValue;
                      if (tooltipText.includes(`Fraction ${fractionNumber}`)) {
                          day.classList.add('highlight');
                      }
                  }
              });
          });

          label.addEventListener('mouseleave', () => {
              calendar.classList.remove('dimmed');
              calendar.querySelectorAll('.highlight').forEach(day => {
                  day.classList.remove('highlight');
              });
          });
      });
  }
});