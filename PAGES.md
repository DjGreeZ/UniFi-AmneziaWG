# Сайт проекта на GitHub Pages

Адрес: <https://djgreez.github.io/UniFi-AmneziaWG/>.

Сайт публикуется из ветки `main`, папки `/docs`. В настройках репозитория: **Settings → Pages → Deploy from a branch → main → /docs → Save**. Папка `docs` содержит готовый статический сайт; её изменения нужно коммитить вместе с исходниками. [Документация GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site).

## Обновление сайта

Генератор использует только стандартную библиотеку Python. Запускайте из корня репозитория:

```console
python scripts/build_site.py
python scripts/check_site.py
```

Исходники находятся в `site/content`, ресурсы — в `site/assets`, описание страниц и версия проекта — в `site/pages.json`. Генератор записывает результат в `docs`; правки готовых HTML-файлов будут заменены при следующей сборке.

Согласованный баннер — `site/assets/banner.png` (1672 × 941). Он используется на главной странице, в README и в Open Graph/Twitter-превью ссылок. Это оформленная обложка проекта; исходный скриншот интерфейса сохранён отдельно в `site/assets/panel.png`. При замене баннера обновите размеры и описания в шаблонах главной, README и `scripts/build_site.py`, затем пересоберите сайт.

После нового релиза обновите версию в `site/pages.json`, метаданные в `CITATION.cff`, инструкции и ссылки в контенте. Указывайте фактическую дату релиза. Затем пересоберите сайт, выполните проверку и просмотрите изменённые страницы. Матрица совместимости должна содержать только подтверждённые сочетания устройств и версий UniFi.

`version` — версия интеграции (сейчас 0.3.2), `awg_config_version` — требуемая версия конфигурации AmneziaWG (сейчас 3.1). Это разные версии. Общая плашка с требованием AWG 3.1 выводится на всех страницах; при изменении требования обновите также инструкции и FAQ на обоих языках.

## Подключение поисковых систем

1. После публикации добавьте в [Google Search Console](https://search.google.com/search-console) ресурс типа **URL-prefix**: `https://djgreez.github.io/UniFi-AmneziaWG/`. Этот тип поддерживает отдельный путь сайта; подтверждение Domain property требует управления DNS. [Типы ресурсов Google](https://support.google.com/webmasters/answer/34592).
2. Получите в сервисе реальный HTML-метатег подтверждения. В `site/verification.json` сохраните значение его атрибута `content` в поле `google`; поле `yandex` предназначено для значения `content` метатега Яндекс Вебмастера. Оставляйте ненастроенные значения пустыми. Не вставляйте весь HTML-тег и не используйте пример вместо выданного значения.
3. Пересоберите и опубликуйте сайт. Убедитесь, что метатеги появились в исходном HTML главной страницы, затем подтвердите права в сервисах. Для Яндекса следуйте [инструкции подтверждения прав](https://yandex.ru/support/webmaster/ru/service/rights); если сервис потребует доступ к корню `djgreez.github.io`, одной публикации в подпапку проекта недостаточно.
4. Отправьте карту сайта `https://djgreez.github.io/UniFi-AmneziaWG/sitemap.xml` в Search Console и [Яндекс Вебмастер](https://webmaster.yandex.ru/). Проверьте главную и основные страницы инструментом проверки URL. [Sitemap Google](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap), [Sitemap Яндекса](https://yandex.ru/support/webmaster/ru/indexing-options/sitemap).

Структура файла подтверждения:

```json
{
  "google": "",
  "yandex": ""
}
```

Значения подтверждения публичны и будут включены в HTML. Само наличие файла с пустыми значениями не подтверждает права на сайт.

## Обнаружение и цитирование

Согласованное ядро запросов распределено по содержанию страниц; частотность пока не измерена:

| Группа | Примеры | Страница |
| --- | --- | --- |
| Общая | Amnezia UniFi, AmneziaWG UniFi, Amnezia на UniFi | Главная |
| Модели | UDM Amnezia, UDR7 Amnezia, UDM Pro AmneziaWG | Установка и совместимость |
| Установка | Как установить Amnezia на UniFi, настройка AmneziaWG на UniFi | Установка |
| Конфиг 3.1 | AmneziaWG 3.1 UniFi, конфиг AWG 3.1 для UniFi, импорт AmneziaWG | Получение конфига и FAQ |
| Практические вопросы | AmneziaWG UniFi не подключается, DNS, VPN для отдельных устройств, резервный сервер | FAQ и архитектура |

Используйте запросы естественно в уникальных title, description, заголовках, ответах и текстах ссылок. Не дублируйте варианты регистра UniFi/UniFI и не создавайте одинаковые страницы для каждой перестановки слов. UDM SE и обычный UDR описываются только как модели с неподтверждённой совместимостью. Google не использует `meta keywords` для индексации и ранжирования: [поддерживаемые метатеги](https://developers.google.com/search/docs/crawling-indexing/special-tags). Уточняйте ядро по фактическим запросам и показам после подключения Search Console.

Добавьте адрес сайта в поле Website раздела About репозитория и в README. Для ссылок на конкретные технические сведения используйте постоянные адреса страниц и якоря разделов; для воспроизводимых инструкций указывайте версию релиза. `CITATION.cff` в корне основной ветки включает в GitHub пункт **Cite this repository** и предоставляет метаданные цитирования. [Файлы CITATION](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-citation-files).

Файл `/UniFi-AmneziaWG/robots.txt` не управляет обходом: поисковые роботы проверяют `https://djgreez.github.io/robots.txt` в корне хоста. Поэтому вложенный robots.txt не нужен; карту сайта можно подать непосредственно в панели вебмастеров. Не меняйте правила корневого сайта без проверки их влияния на другие проекты. [Правила robots.txt](https://developers.google.com/crawling/docs/robots-txt/robots-txt-spec).

Публикация сайта и отправка sitemap не гарантируют индексацию, позиции или цитирование. Google Search не использует `llms.txt` для улучшения видимости; специальный файл для ИИ не требуется. Основная работа — полезные и проверенные инструкции, доступные HTML-страницы, корректные ссылки и актуальные сведения о проекте. [Рекомендации Google для поиска с ИИ](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide).
