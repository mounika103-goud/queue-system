/**
 * Skeleton Loader Utility
 * Create and manage skeleton loaders for smooth loading states
 */

class SkeletonLoader {
    static createTextSkeleton(lines = 3, width = '100%') {
        const container = document.createElement('div');
        for (let i = 0; i < lines; i++) {
            const skeleton = document.createElement('div');
            skeleton.className = 'skeleton skeleton-text';
            skeleton.style.width = i === lines - 1 ? '80%' : width;
            if (i > 0) skeleton.style.marginTop = '8px';
            container.appendChild(skeleton);
        }
        return container;
    }

    static createCardSkeleton() {
        const card = document.createElement('div');
        card.className = 'card';
        
        const cardBody = document.createElement('div');
        cardBody.className = 'card-body';
        
        const heading = document.createElement('div');
        heading.className = 'skeleton skeleton-heading';
        heading.style.width = '70%';
        
        const text = this.createTextSkeleton(2);
        
        cardBody.appendChild(heading);
        cardBody.appendChild(text);
        card.appendChild(cardBody);
        
        return card;
    }

    static createKPISkeleton() {
        const card = document.createElement('div');
        card.className = 'kpi-card skeleton-loader kpi-card';
        card.style.height = '180px';
        
        const heading = document.createElement('div');
        heading.className = 'skeleton skeleton-heading';
        heading.style.width = '60%';
        
        const value = document.createElement('div');
        value.className = 'skeleton';
        value.style.height = '32px';
        value.style.width = '40%';
        value.style.marginBottom = '8px';
        
        const text = document.createElement('div');
        text.className = 'skeleton skeleton-text';
        text.style.width = '50%';
        
        card.appendChild(heading);
        card.appendChild(value);
        card.appendChild(text);
        
        return card;
    }

    static createTableSkeleton(rows = 5, cols = 4) {
        const table = document.createElement('table');
        table.className = 'table skeleton-loader table';
        
        const thead = document.createElement('thead');
        const headerRow = document.createElement('tr');
        
        for (let i = 0; i < cols; i++) {
            const th = document.createElement('th');
            const skeleton = document.createElement('div');
            skeleton.className = 'skeleton skeleton-text';
            skeleton.style.width = '80%';
            th.appendChild(skeleton);
            headerRow.appendChild(th);
        }
        thead.appendChild(headerRow);
        table.appendChild(thead);
        
        const tbody = document.createElement('tbody');
        for (let i = 0; i < rows; i++) {
            const row = document.createElement('tr');
            for (let j = 0; j < cols; j++) {
                const td = document.createElement('td');
                const skeleton = document.createElement('div');
                skeleton.className = 'skeleton skeleton-text';
                skeleton.style.width = '90%';
                td.appendChild(skeleton);
                row.appendChild(td);
            }
            tbody.appendChild(row);
        }
        table.appendChild(tbody);
        
        return table;
    }

    static createGridSkeleton(items = 6) {
        const container = document.createElement('div');
        container.className = 'skeleton-grid';
        
        for (let i = 0; i < items; i++) {
            const item = document.createElement('div');
            item.className = 'card';
            
            const img = document.createElement('div');
            img.className = 'skeleton';
            img.style.height = '180px';
            img.style.marginBottom = '16px';
            
            const body = document.createElement('div');
            body.className = 'card-body';
            
            const heading = document.createElement('div');
            heading.className = 'skeleton skeleton-heading';
            heading.style.width = '60%';
            
            const text = this.createTextSkeleton(2);
            
            body.appendChild(heading);
            body.appendChild(text);
            item.appendChild(img);
            item.appendChild(body);
            
            container.appendChild(item);
        }
        
        return container;
    }

    static createListSkeleton(items = 5) {
        const container = document.createElement('div');
        
        for (let i = 0; i < items; i++) {
            const item = document.createElement('div');
            item.style.marginBottom = '16px';
            item.style.padding = '12px';
            item.style.borderRadius = '8px';
            item.style.backgroundColor = '#f8f9fa';
            
            const avatar = document.createElement('div');
            avatar.className = 'skeleton skeleton-avatar';
            avatar.style.marginRight = '12px';
            avatar.style.display = 'inline-block';
            avatar.style.marginBottom = '0';
            
            const content = document.createElement('div');
            content.style.display = 'inline-block';
            content.style.width = 'calc(100% - 60px)';
            content.style.verticalAlign = 'top';
            
            const heading = document.createElement('div');
            heading.className = 'skeleton skeleton-text';
            heading.style.width = '40%';
            heading.style.marginBottom = '4px';
            
            const text = document.createElement('div');
            text.className = 'skeleton skeleton-text';
            text.style.width = '60%';
            
            content.appendChild(heading);
            content.appendChild(text);
            item.appendChild(avatar);
            item.appendChild(content);
            
            container.appendChild(item);
        }
        
        return container;
    }

    static showSkeleton(element, type = 'card', options = {}) {
        const placeholder = document.createElement('div');
        placeholder.className = 'skeleton-placeholder';
        placeholder.dataset.skeletonType = type;
        
        let skeleton;
        switch (type) {
            case 'card':
                skeleton = this.createCardSkeleton();
                break;
            case 'kpi':
                skeleton = this.createKPISkeleton();
                break;
            case 'table':
                skeleton = this.createTableSkeleton(options.rows, options.cols);
                break;
            case 'grid':
                skeleton = this.createGridSkeleton(options.items);
                break;
            case 'list':
                skeleton = this.createListSkeleton(options.items);
                break;
            case 'text':
                skeleton = this.createTextSkeleton(options.lines, options.width);
                break;
            default:
                skeleton = this.createCardSkeleton();
        }
        
        placeholder.appendChild(skeleton);
        element.innerHTML = '';
        element.appendChild(placeholder);
        
        return placeholder;
    }

    static hideSkeleton(element) {
        const placeholder = element.querySelector('.skeleton-placeholder');
        if (placeholder) {
            placeholder.classList.add('fade-out');
            setTimeout(() => placeholder.remove(), 300);
        }
    }

    static replaceSkeleton(element, content) {
        const placeholder = element.querySelector('.skeleton-placeholder');
        if (placeholder) {
            placeholder.classList.add('fade-out');
            setTimeout(() => {
                placeholder.remove();
                const newContent = document.createElement('div');
                newContent.classList.add('fade-in');
                newContent.innerHTML = content;
                element.appendChild(newContent);
            }, 300);
        } else {
            const newContent = document.createElement('div');
            newContent.classList.add('fade-in');
            newContent.innerHTML = content;
            element.appendChild(newContent);
        }
    }
}

// Export for use in other scripts
if (typeof window !== 'undefined') {
    window.SkeletonLoader = SkeletonLoader;
}
