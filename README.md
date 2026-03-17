# doughboy
doughboyはNotionのデータソースを容易に扱うために開発されたPythonモジュールです。構文はSQLAlchemyモジュールを参考にしています。


# インストール方法
pipモジュールを利用してインストールします。標準のrequestsモジュールを利用していますが、uv pipを利用している場合などでは追加インストールを求められる場合があります。

```
pip install doughboy
```

# 準備
doughboyモジュールを利用するために必要な準備について説明します。

## doughboyモジュールを生成する
すべてのアクセスはdoughboyオブジェクトを介して行なわれます。NotionのAPIキーを引数にdoughboyオブジェクトを生成します。

```
from doughboy import *

apikey = "ntn_*****************"
db = doughboy(apikey)
```

従来、Notionでは"secret_"で始まるAPIキーを利用していましたが、これはすでに古い形式となっています。利用に支障はありませんが、ファイルアップロードAPIなどに対応していません。doughboyモジュールではエラーとしていますので"ntn_"で始まる新しい形式のAPIキーが必要です。

## データソースモデルを定義する
doughboyオブジェクトはデータソースモデルを介してNotionのデータソースへアクセスします。データソースデモルはdata_sourceクラスを派生させて定義します。

titleプロパティとrich_textプロパティを持ったNotionのデータソースがある場合、データソースモデルはpropsクラスを使い、次のように定義します。__data_source_id__メンバにはNoiton上で取得できるデータソースIDをかならず指定します。

```
class ds_test(data_source):
    __data_source_id__ = "********-****-****-****-************"

    title = props("title", title_prop)
    text = props("text", rich_text_prop)
```

propsクラスの第一引数には実際のデータソースに付与したプロパティ名を、第二引数にはプロパティタイプクラスを指定します。プロパティタイプクラスはNotionのプロパティタイプ名に_propをつけたもので統一されています。現在対応しているプロパティタイプクラスは次の通りです。

- title_prop
- rich_text_prop
- date_prop
- number_prop
- select_prop
- multi_select_prop
- status_prop
- people_prop
- checkbox_prop
- url_prop
- email_prop
- phone_number_prop
- relation_prop
- file_prop(対応中)

クラスメンバ変数名はNotionデータソースのプロパティ名と同じにします。

# データソース全体を操作する
doughboyではデータソース内のページを一括処理することができます。その操作手順を説明していきます。

## データソースページを取得する
データソースに登録されているページを取得するにはselect_fromメソッドを利用します。絞り込み条件やソート条件を指定しない場合は続けてexecメソッドを呼び出します。

```
pages = db.select_from(ds_test).exec()
for page in pages:
   print(f"title: {page.title.value}, text) 
```

絞り込み条件とソート条件を指定する場合は、次のように記述します。具体的な条件の指定方法はこの後に説明します。

```
page = db.select_from(データソースモデル).where(絞り込み条件).order_by(ソート条件).exec()
```

### 絞り込み条件を指定する
取得するページを絞り込むにはwhereメソッドを用います。絞り込み条件はデータソースモデルに定義したクラスメンバ変数を用いて設定します。たとえば、titleプロパティが"hoge"というページを取得したい場合はequalsメソッドを用いて次のように記述します。

```
pages = db.select_from(ds_test).where(ds_test.title.equals("hoge")).exec()
for page in pages:
   print(f"title: {page.title.value}, text) 
```

Notionのデータソースは一般的なデータベースシステムが持つテーブルとは異なり、一意な価を持つ主キーという概念がないため、複数のページが取得されることがあります。

titleプロパティが"hoge"で始まるページを取得したい場合は、startswithメソッドを用いて指定します。

```
pages = db.select_from(ds_test).where(ds_test.title.startswith("hoge")).exec()
```

doughboyにはNotion APIのquery data sourceで指定可能なfilterと同名のメソッドを用意してあります。現在対応しているメソッドは次の通りです。

- after
- any
- before
- contains
- does_not_contain
- does_not_equals
- ends_with
- equals
- every
- greater_than
- greater_than_or_equal_to
- is_empty
- is_not_empty
- less_than
- less_than_or_equal_to
- next_month
- next_week
- next_year
- none
- on_or_after
- on_or_before
- past_month
- past_week
- past_year
- starts_with
- this_week

また、いくつかのメソッドは比較演算子でオーバーライドしてあります。たとえばequalsメソッドは等価演算子（==）でも代用できます。

```
pages = db.select_from(ds_test).where(ds_test.title == "hoge").exec()
```

### 複数の絞り込み条件を指定する
複数の絞り込み条件を指定したい場合はor_メソッド、and_メソッドを利用します。次の例ではtitleプロパティが"hoge"または"piyo"のものを取得しています。

```
pages = db.select_from(ds_test).where(or_(ds_test.title == "hoge", ds_test.title == "piyo")).exec()
```

### ソート条件を指定する
select_fromメソッドで取得するページ順を並べ替えられます。orer_byメソッドを用い、並べ替えるプロパティ順にソート順序を指定します。ソート順序はasc_メソッド（昇順）、desc_メソッド（降順）があります。ロングネームを好む方のためにascendingメソッドとdescendingメソッドも存在します。

```
pages = db.select_from(ds_test).order_by(asc_(ds_test.title), desc_(ds_test.text)).exec()
```

# 取得カラムの絞り込み
select_fromメソッドが返すページオブジェクト内のプロパティを絞り込めます。次の例ではtextプロパティのみが結果オブジェクトに含まれるようになります。

```
pages = db.select_from(ds_test.text).exec()
```

複数のプロパティを取得したい場合はカンマで区切って指定します。

```
pages = db.select_from(ds_test.title, ds_test.text).exec()
```

ds_testデータソースは2つのプロパティしか存在しないため、以下のどちらを利用しても同じ結果を返します。

```
pages = db.select_from(ds_test).exec()
pages = db.select_from(ds_test.title, ds_test.text).exec()
```

## データソースページを更新する
update_toメソッドを用いるとデータベースページの内容を一括して更新できます。update_toメソッドにデータソースクラスを指定し、valuesメソッドにプロパティの更新内容を記述します。

```
db.update_to(データソースモデル).values(title="updated hoge", text="updated text")
```

通常はwhereメソッドで条件を絞り込んで使います。絞り込み条件を指定しない場合、データソース内にあるページすべてを更新します。

```
db.update_to(データソースモデル).where(絞り込み条件).values(更新内容)
```

## データソースページを削除する
delete_fromメソッドを用いるとデータベースページを削除し、ゴミ箱へ捨てます。delete_fromメソッドにデータソースクラスを指定し、execメソッドを呼び出します。

```
db.delete_from(データソースモデル).exec()
```

通常はwhereメソッドで条件を絞り込んで使います。絞り込み条件を指定しない場合、データソース内にあるページすべてを削除します。

```
db.delete_from(データソースモデル).where(絞り込み条件)exec()
```

## データソースページを追加する
insert_intoメソッドを用いると新しいデータソースページを追加できます。このメソッドのみ例外で、データソースページ単体の操作となります。insert_intoメソッドにデータソースクラスを指定し、valuesメソッドにプロパティ値を記述します。

```
db.insert_into(ds_test).values(title="new page title", text="new page text")
```

# データソースページごとに操作する
select_fromメソッドの返すデータソースページ個別に操作するためのメソッドが2つ用意されています。次からそれらのメソッドについて説明します。

## データソースページを更新する
update_oneメソッドを用いると指定したデータベースページを更新できます。データソースページ内のプロパティ値を変更したい場合はvalueプロパティを利用します。次の例ではselect_fromメソッドで取得されたすべてのページについて、titleプロパティの値、およびtextプロパティの値を変更し、update_oneメソッドを用いて実際のデータソースページを更新しています。

```
pages = db.select_from(ds_test).where(ds_test.title == "hoge").exec()
for page in pages:
    page.title.value = "new title"
    page.text.value = "new text"
    db.update_one(page)
```

## データソースページを削除する
delete_oneメソッドを用いると指定したデータベースページを削除してゴミ箱へ入れます。

```
db.delete_one(page)
```
