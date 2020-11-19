function toggleClass(elem, className){
                if (elem.className.indexOf(className) !== -1){
                    elem.className = elem.className.replace(className,'');
                }
                else {
                    elem.className = elem.className.replace(/\s+/g,' ') +   ' ' + className;
                }
                return elem;
            }

            function toggleDisplay(elem){
                const curDisplayStyle = elem.style.display;         
                            
                if (curDisplayStyle === 'none' || curDisplayStyle === ''){
                    elem.style.display = 'block';
                }
                else{
                    elem.style.display = 'none';
                }
            }

        function toggleMenuDisplay(e){
            const dropdown = e.currentTarget.parentNode;
            const menu = dropdown.querySelector('.plot-wrapper');

            toggleClass(menu, 'hide');
        }


        //get elements
        const tDropdownTitle = document.querySelector('.wrapper#temp .info');
        const uDropdownTitle = document.querySelector('.wrapper#u .info');
        const pDropdownTitle = document.querySelector('.wrapper#pres .info');

        //bind listeners to these elements
        tDropdownTitle.addEventListener('click', toggleMenuDisplay);
        uDropdownTitle.addEventListener('click', toggleMenuDisplay);
        pDropdownTitle.addEventListener('click', toggleMenuDisplay);