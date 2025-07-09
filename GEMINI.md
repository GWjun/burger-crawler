아래의 스키마를 참고해서 답변해줘

```prisma
model Nutrition {
product_id BigInt @id @default(autoincrement())
calories Decimal? @db.Decimal
fat Decimal? @db.Decimal
protein Decimal? @db.Decimal
sugar Decimal? @db.Decimal
sodium Decimal? @db.Decimal
created_at DateTime @default(now()) @db.Timestamptz(6)
Products Product @relation(fields: [product_id], references: [product_id], onDelete: NoAction, onUpdate: NoAction)
}

model Brand {
id BigInt @id(map: "Brands_pkey") @default(autoincrement())
name String @unique @db.VarChar
description String?
logo_url String? @db.VarChar
website_url String? @db.VarChar
created_at DateTime @default(now()) @db.Timestamptz(6)
likes_count Int @default(0)
name_eng String @unique @db.VarChar
background_image_url String? @db.VarChar
BrandLike BrandLike[]
Product Product[]
}

model Product {
product_id BigInt @id(map: "Products_pkey") @default(autoincrement())
created_at DateTime @default(now()) @db.Timestamptz(6)
name String @db.VarChar
description String?
image_url String? @db.VarChar
price Int
available Boolean? @default(true)
category String? @db.VarChar
shop_url String? @db.VarChar
set_price Int?
description_full String?
released_at DateTime? @db.Timestamptz(6)
brand_name String @db.VarChar
likes_count Int @default(0)
dislikes_count Int @default(0)
patty Patty @default(undefined)
dev_comment String? @db.VarChar
review_count Int @default(0)
score_avg Float @default(0) @db.Real
Nutrition Nutrition?
Brand Brand @relation(fields: [brand_name], references: [name], onDelete: NoAction, onUpdate: NoAction)
ProductLike ProductLike[]
Review Review[]
}

enum Patty {
meat
shrimp
chicken
squid
vegan
undefined
}
```
