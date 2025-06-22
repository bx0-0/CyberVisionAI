  // تهيئة JointJS
  const graph = new joint.dia.Graph();
  const paper = new joint.dia.Paper({
      el: document.getElementById('paper'),
      model: graph,
      width: '100%',
      height: '100%',
      gridSize: 10,
      drawGrid: true,
      background: {
          color: '#f5f5f5'
      }
  });

  // تعريف الأشكال
  const shapes = {
      router: {
          shape: joint.shapes.basic.Image,
          size: { width: 120, height: 60 },
          attrs: {
              image: { 'xlink:href': '../static/img/router.png', width: 120, height: 60 },
              label: { text: 'router', fill: 'black', 'font-size': 12, 'ref-y': 45 }
          }
      },
      switch: {
          shape: joint.shapes.basic.Image,
          size: { width: 120, height: 60 },
          attrs: {
              image: { 'xlink:href': '../static/img/switch.png', width: 120, height: 60 },
              label: { text: 'switch', fill: 'black', 'font-size': 12, 'ref-y': 45 }
          }
      },
      pc: {
          shape: joint.shapes.basic.Image,
          size: { width: 120, height: 60 },
          attrs: {
              image: { 'xlink:href': '../static/img/pc.png', width: 120, height: 60 },
              label: { text: 'pc', fill: 'black', 'font-size': 12, 'ref-y': 45 }
          }
      },
      server: {
          shape: joint.shapes.basic.Image,
          size: { width: 120, height: 60 },
          attrs: {
              image: { 'xlink:href': '../static/img/server.png', width: 120, height: 60 },
              label: { text: 'server', fill: 'black', 'font-size': 12, 'ref-y': 45 }
          }
      }
  };
  // دالة لإنشاء ID فريد
const generateUniqueId = (nameOfShap) => {
    return nameOfShap+'-' + Math.random().toString(36).substr(2, 9);
};

  // إضافة الأشكال الثابتة إلى منطقة الرسم
  const router = new shapes.router.shape({
      position: { x: 50, y: 50 },
      size: shapes.router.size,
      attrs: shapes.router.attrs
  });

  const switchElement = new shapes.switch.shape({
      position: { x: 200, y: 50 },
      size: shapes.switch.size,
      attrs: shapes.switch.attrs
  });

  const pc = new shapes.pc.shape({
      position: { x: 350, y: 50 },
      size: shapes.pc.size,
      attrs: shapes.pc.attrs
  });

  const server = new shapes.server.shape({
      position: { x: 500, y: 50 },
      size: shapes.server.size,
      attrs: shapes.server.attrs
  });

  // إضافة ID فريد لكل شكل
router.set('id', generateUniqueId("router"));
switchElement.set('id', generateUniqueId("switch"));
pc.set('id', generateUniqueId("pc"));
pc.set('id', generateUniqueId("server"));

  graph.addCells([router, switchElement, pc, server]);

  // جعل الأشكال الثابتة
  router.set('locked', true);
  switchElement.set('locked', true);
  pc.set('locked', true);
  server.set('locked', true);

// نسخ العناصر عند النقر بزر الفأرة الأيسر
paper.on('cell:pointerdown', (cellView, evt) => {
    if (evt.button === 0) { // زر الفأرة الأيسر
        const originalElement = cellView.model;

        // التحقق مما إذا كان العنصر ثابتًا (Router، Switch، PC)
        if (originalElement.get('locked')) {
            // إنشاء نسخة من العنصر
            const copy = originalElement.clone();
            copy.set('position', {
                x: originalElement.attributes.position.x + 20,
                y: originalElement.attributes.position.y + 20
            });
            copy.set('locked', false); // السماح بتحريك النسخة
            const shapeId = generateUniqueId(copy.attributes.attrs.label.text.toLowerCase()); // إنشاء ID فريد للنسخة
            copy.set('id', shapeId); // إضافة ID فريد للنسخة

            // إنشاء مكان في localStorage باستخدام ID الشكل كـ key
            if (!localStorage.getItem(shapeId)) {
                localStorage.setItem(shapeId, JSON.stringify([])); // تخزين array فارغ
            }

            graph.addCell(copy);
        }
    }
});

  // سلة المهملات
  const trash = document.getElementById('trash');

  // تفعيل سلة المهملات
  paper.on('cell:pointerup', (cellView) => {
      const element = cellView.model;
      const trashRect = trash.getBoundingClientRect();
      const elementRect = cellView.el.getBoundingClientRect();

      // التحقق مما إذا كان الشكل فوق سلة المهملات
      if (
          elementRect.left < trashRect.right &&
          elementRect.right > trashRect.left &&
          elementRect.top < trashRect.bottom &&
          elementRect.bottom > trashRect.top
      ) {
          if (!element.get('locked')) { // التأكد من أن العنصر غير ثابت
              element.remove(); // حذف العنصر
          }
      }
  });

  // تفعيل الربط بين العناصر
  const linkButton = document.getElementById('link-button');
  let linkingMode = false;
  let sourceElement = null;
  let tempLink = null;

  linkButton.addEventListener('click', () => {
      linkingMode = !linkingMode; // تبديل وضع الربط
      linkButton.textContent = linkingMode ? 'Stop Linking' : 'Link';
  });

  paper.on('cell:pointerdown', (cellView) => {
      if (linkingMode) {
          if (!sourceElement) {
              sourceElement = cellView.model;

              // إنشاء خط مؤقت
              tempLink = new joint.shapes.standard.Link({
                  source: { id: sourceElement.id },
                  target: { x: cellView.model.attributes.position.x, y: cellView.model.attributes.position.y },
                  attrs: {
                      line: { stroke: 'black', strokeWidth: 2, strokeDasharray: '5 5' }
                  }
              });
              graph.addCell(tempLink);
          } else {
              const targetElement = cellView.model;

              if (sourceElement && targetElement && sourceElement.id !== targetElement.id) {
                  // إنشاء وصلة دائمة
                  const link1 = new joint.shapes.standard.Link({
                      source: { id: sourceElement.id },
                      target: { id: targetElement.id },
                      attrs: {
                          line: { stroke: 'black', strokeWidth: 2 }
                      }
                  });
                  const link2 = new joint.shapes.standard.Link({
                      source: { id: targetElement.id },
                      target: { id: sourceElement.id },
                      attrs: {
                          line: { stroke: 'black', strokeWidth: 2 }
                      }
                  });
                  graph.addCell(link1);
                  graph.addCell(link2);
              }

              // إعادة تعيين الحالة
              linkingMode = false;
              linkButton.textContent = 'Link';
              sourceElement = null;
              if (tempLink) {
                  tempLink.remove(); // حذف الخط المؤقت
              }
          }
      }
  });


const getShapeTypeFromId = (shapeId) => {
    const parts = shapeId.split('-');
    return parts[0];
};


// دالة لتحميل المهام من localStorage
const loadTask = (shapeId) => {
    const modal = document.getElementById('modal');
    const modalTitle = document.getElementById('modal-title');
    const taskList = document.getElementById('task-list'); // مكان عرض المهام

    // مسح المهام الحالية
    taskList.innerHTML = '';

    // جلب المهام من localStorage باستخدام id الشكل كـ key
    const tasks = JSON.parse(localStorage.getItem(shapeId)) || [];

    // عرض المهام
    tasks.forEach((task, index) => {
        const taskItem = document.createElement('div');
        taskItem.className = 'task-item';

        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.id = `task-${index}`;
        checkbox.checked = task.checked;

        const label = document.createElement('label');
        label.htmlFor = `task-${index}`;
        label.textContent = ` ${task.text}`;

        // تحديث حالة المهمة عند التحديد
        checkbox.addEventListener('change', () => {
            tasks[index].checked = checkbox.checked;
            localStorage.setItem(shapeId, JSON.stringify(tasks));
        });

        taskItem.appendChild(checkbox);
        taskItem.appendChild(label);
        taskList.appendChild(taskItem);
    });

    // عرض النافذة
    modalTitle.textContent = `Element Details - ${shapeId}`;
    modal.style.display = 'block';
};






// تفعيل القائمة
const menuButton = document.getElementById('menu-button');
const closeButton = document.getElementById('close-button');

let menuMode = false;

menuButton.addEventListener('click', () => {
    menuMode = !menuMode; // تبديل وضع القائمة
    menuButton.textContent = menuMode ? 'Stop Menu' : 'Menu';
});

paper.on('cell:pointerdown', (cellView) => {
    if (menuMode) {
        const element = cellView.model;
        const shapeId = element.get('id'); // الحصول على ID الخاص بالشكل

        checkTask(shapeId,getShapeTypeFromId(shapeId));
        // تحميل المهام الخاصة بالشكل
        loadTask(shapeId);

        menuMode = false; // إيقاف وضع القائمة
        menuButton.textContent = 'Menu';
    }
});

// إغلاق النافذة
closeButton.addEventListener('click', () => {
    modal.style.display = 'none';
});


  