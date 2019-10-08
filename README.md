# Toonproject

Odoo 12 addon for project management in animation industry,
work in progress.

## Instalation

Clone this repository to your Odoo addons folder as **toonproject**.

## To be done

* [x] Команда для объединения нескольких задач в одну ~~ветка [combine_tasks_wizard](../../tree/combine_tasks_wizard)~~ - закончено.
* [x] Дополнительный статус задачи "поправки" (даже два статуса: "поправки" и "в поправках" -- до и после того, как исполнитель увидел правки и принялся за их выполнение) -- закончено.
* [ ] Разные единицы измерения метража (кадры/секунды/минуты) - ветка [measure_units](../../tree/measure_units)
* [ ] **Общий механизм загрузки видео и исходников** (включая разграничение прав на эту операцию) - ветка [file_fields](../../tree/file_fields)
#### Коннекторы:
  * [ ] Коннектор с Owncloud (через Webdav)
  * [ ] Коннектор с Syncsketch (пока неизвестно, как)
  * [ ] Коннектор с Synology (через Webdav или FTP?..)
  * [ ] Коннектор с Keyframe Pro (пока в порядке бреда; Keyframe Pro сохраняет проекты в читабельном формате JSON, можно было бы сделать online-читалку для этих проектов. Правда, к Odoo это прямого отношения не имеет, и это совсем не просто. Но это проще, чем создавать с нуля новый Syncsketch.)
  * [ ] Коннектор с [videojs-annotation-comments](https://github.com/contently/videojs-annotation-comments) (и доработка последнего)
####
* [ ] **Разграничение прав по проектам**
* [ ] Подсчет общего количества заданий у каждого исполнителя единовременно (с запретом брать больше определенного количества)
* [ ] Команды для фиксации факта оплаты работы, в т.ч. механизм фиксации стоимости в момент оплаты.
* [x] Скрывать стоимость от работников, не имеющих отношения к данному процессу (не менеджер и не (потенциальный)исполнитель данного задания)
* [ ] Логика использования поля "прогнозируемое завершение"
* [ ] Просмотр сцен в монтаже через плэйлист (монтируются preview разных ассетов и разных заданий) -- в большей степени Javascript, чем непосредственно Odoo

#### Макросы для убыстрения работы администратора
* [ ] Команда для добавления к влияющим задачам аналогичной задачи по предыдущей (по монтажу) сцены. 
* [ ] Автоматическое добавление к влияющим задачам задач по незаконченным ригам и фонам при добавлении соответствующих материалов в список материалов сцены
* [ ] Сводка свойств задачи для отсылки еще незарегистрированным работникам (для тестовых сцен соискателям работы)
* [ ] Наглядное отображение зависимостей между задачами (цепочки взаимозависимых задач одного типа (монтажных сцен, которые следует отдавать одному аниматору) и определение первостепенности задач, которые сильно задерживают другие задачи)

#### Украшательства (опционально)
* [ ] Альтернативный виджет Many2many (подобный виджету Many2many_tags) для компактного отображения списков материалов и зависимых задач в окне формы задачи (ветка [many2many_alter_widget](../../tree/many2many_alter_widget))
* [x] Цветовая дифференциация ~штанов~ фона строк в списках задач и материалов - сделано для материалов. Для задач -- обойдемся канбаном.
* [ ] Дашборд в дизайне Канбана (скорее всего, это вообще невозможно) ветка [kanban_dashboard](../../tree/kanban_dashboard)
* [ ] Как вариант -- несколько разных пунктов меню для задач в проверку, в работу, в работе и в оплату для данного юзера. 
* [ ] Отображение временной шкалы -- кто какой задачей сколько занимался (определяеть по датам смены статуса, в том числе и для контролеров)
* [ ] Более удобное отображение на мобильных устройствах
