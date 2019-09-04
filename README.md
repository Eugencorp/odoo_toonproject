# Toonproject

Odoo 12 addon for project management in animation industry,
work in progress.

## Instalation

Clone this repository to your Odoo addons folder as toonproject.

## To be done

* [x] Команда для объединения нескольких задач в одну ~~(ветка [combine_tasks_wizard](../../tree/combine_tasks_wizard))~~ - закончено.
* [ ] Дополнительный статус задачи "поправки" (возможно, даже два статуса: "поправки" и "в поправках" -- до и после того, как исполнитель увидел правки и принялся за их выполнение)
* [ ] Разные единицы измерения метража (кадры/секунды/минуты)
* [ ] **Общий механизм загрузки видео и исходников** (включая разграничение прав на эту операцию)
#### Коннекторы:
  * [ ] Коннектор с Owncloud (через Webdav) ветка [file_upload](../../tree/file_upload)
  * [ ] Коннектор с Syncsketch (пока неизвестно, как)
  * [ ] Коннектор с Synology (через Webdav или FTP?..)
  * [ ] Коннектор с Keyframe Pro (пока в порядке бреда)
####
* [ ] **Разграничение прав по проектам**
* [ ] Подсчет общего количества заданий у каждого исполнителя единовременно (с запретом брать больше определенного количества)
* [ ] Команды для фиксации факта оплаты работы, в т.ч. механизм фиксации стоимости в момент оплаты.
* [ ] Логика использования поля "прогнозируемое завершение"

#### Украшательства (опционально)
* [ ] Альтернативный виджет Many2many (подобный виджету Many2many_tags) для компактного отображения списков материалов и зависимых задач в окне формы задачи (ветка [many2many_alter_widget](../../tree/many2many_alter_widget))
* [ ] Цветовая дифференциация ~штанов~ фона строк в списках задач и материалов
* [ ] Дашборд в дизайне Канбана (скорее всего, это вообще невозможно) ветка [kanban_dashboard](../../tree/kanban_dashboard)
