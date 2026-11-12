<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import BrandMark from './components/BrandMark.vue'
import FeatureIcon from './components/FeatureIcon.vue'

type Cat = {
  id: string
  name: string
  photo: string
  breed: string
  birthday: string
  gender: string
  personality: string
  notes: string
  createdAt: string
  updatedAt: string
}

type CatForm = Omit<Cat, 'id' | 'createdAt' | 'updatedAt'>
type View = 'home' | 'list' | 'form' | 'detail'

const emptyForm = (): CatForm => ({
  name: '', photo: '', breed: '', birthday: '', gender: '', personality: '', notes: '',
})

const cats = ref<Cat[]>([])
const view = ref<View>('home')
const selectedId = ref('')
const form = ref<CatForm>(emptyForm())
const editingId = ref('')
const nameError = ref('')
const photoError = ref('')
const storageError = ref('')
const notice = ref('')
const isSaving = ref(false)
const isReadingPhoto = ref(false)
const search = ref('')

const selectedCat = computed(() => cats.value.find((cat) => cat.id === selectedId.value) ?? null)
const visibleCats = computed(() => {
  const query = search.value.trim().toLocaleLowerCase()
  if (!query) return cats.value
  return cats.value.filter((cat) => `${cat.name} ${cat.breed}`.toLocaleLowerCase().includes(query))
})

async function loadCats() {
  try {
    const response = await fetch(`${apiBaseUrl}/api/cats`)
    if (!response.ok) throw new Error(`服务器返回错误（HTTP ${response.status}）`)
    cats.value = await response.json() as Cat[]
    storageError.value = ''
  } catch (error) {
    storageError.value = error instanceof Error
      ? `读取档案失败：${error.message}。请检查后端并重试。`
      : '读取档案失败。请检查后端并重试。'
  }
}

function syncRoute() {
  const path = window.location.hash.replace(/^#/, '')
  const detailMatch = path.match(/^\/cats\/([^/]+)$/)
  if (path === '/cats/new') {
    view.value = 'form'
    selectedId.value = ''
  } else if (detailMatch) {
    view.value = 'detail'
    selectedId.value = decodeURIComponent(detailMatch[1])
  } else if (path === '/cats') {
    view.value = 'list'
    selectedId.value = ''
  } else {
    view.value = 'home'
    selectedId.value = ''
  }
}

function navigate(path: string) {
  if (window.location.hash === `#${path}`) syncRoute()
  else window.location.hash = path
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function startNewCat() {
  editingId.value = ''
  form.value = emptyForm()
  nameError.value = ''
  photoError.value = ''
  notice.value = ''
  navigate('/cats/new')
}

function editCat(cat: Cat) {
  editingId.value = cat.id
  form.value = {
    name: cat.name,
    photo: cat.photo,
    breed: cat.breed,
    birthday: cat.birthday,
    gender: cat.gender,
    personality: cat.personality,
    notes: cat.notes,
  }
  nameError.value = ''
  photoError.value = ''
  notice.value = ''
  navigate('/cats/new')
}

function openCat(cat: Cat) {
  navigate(`/cats/${encodeURIComponent(cat.id)}`)
}

function isValidImage(file: File) {
  return file.type === 'image/jpeg' || file.type === 'image/png' || file.type === 'image/webp' || file.type === 'image/gif'
}

function readPhoto(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  photoError.value = ''
  if (!file) return
  if (!isValidImage(file)) {
    photoError.value = '请选择 JPG、PNG、WebP 或 GIF 图片。'
    input.value = ''
    return
  }
  if (file.size > 8 * 1024 * 1024) {
    photoError.value = '图片请小于 8 MB。'
    input.value = ''
    return
  }

  isReadingPhoto.value = true
  const reader = new FileReader()
  reader.onload = () => {
    const source = new Image()
    source.onload = () => {
      const scale = Math.min(1, 1000 / Math.max(source.width, source.height))
      const canvas = document.createElement('canvas')
      canvas.width = Math.max(1, Math.round(source.width * scale))
      canvas.height = Math.max(1, Math.round(source.height * scale))
      const context = canvas.getContext('2d')
      if (!context) {
        photoError.value = '暂时无法处理这张图片，请换一张试试。'
      } else {
        context.drawImage(source, 0, 0, canvas.width, canvas.height)
        form.value.photo = canvas.toDataURL('image/jpeg', 0.82)
      }
      isReadingPhoto.value = false
    }
    source.onerror = () => {
      photoError.value = '图片读取失败，请换一张试试。'
      isReadingPhoto.value = false
    }
    source.src = String(reader.result)
  }
  reader.onerror = () => {
    photoError.value = '图片读取失败，请换一张试试。'
    isReadingPhoto.value = false
  }
  reader.readAsDataURL(file)
}

function removePhoto() {
  form.value.photo = ''
  photoError.value = ''
}

async function saveCat() {
  nameError.value = ''
  photoError.value = ''
  storageError.value = ''
  const name = form.value.name.trim()
  if (!name) {
    nameError.value = '请填写猫咪名字。'
    document.getElementById('cat-name')?.focus()
    return
  }
  if (isReadingPhoto.value) {
    photoError.value = '照片还在处理中，请稍等一下。'
    return
  }

  isSaving.value = true
  notice.value = ''
  await new Promise((resolve) => window.setTimeout(resolve, 120))
  const previous = cats.value.find((cat) => cat.id === editingId.value)
  try {
    const response = await fetch(
      previous ? `${apiBaseUrl}/api/cats/${encodeURIComponent(previous.id)}` : `${apiBaseUrl}/api/cats`,
      {
        method: previous ? 'PUT' : 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...form.value, name }),
      },
    )
    if (!response.ok) throw new Error(`服务器返回错误（HTTP ${response.status}）`)
    const savedCat = await response.json() as Cat
    cats.value = previous
      ? cats.value.map((cat) => cat.id === previous.id ? savedCat : cat)
      : [savedCat, ...cats.value]
    isSaving.value = false
    notice.value = previous ? '修改已保存。' : '档案已保存。'
    openCat(savedCat)
  } catch (error) {
    isSaving.value = false
    storageError.value = error instanceof Error
      ? `保存失败：${error.message}。你填写的内容还在，可以重试。`
      : '保存失败。你填写的内容还在，可以重试。'
  }
}

async function deleteCat(cat: Cat) {
  if (!window.confirm(`确定删除「${cat.name}」的档案吗？删除后无法恢复。`)) return
  try {
    const response = await fetch(`${apiBaseUrl}/api/cats/${encodeURIComponent(cat.id)}`, { method: 'DELETE' })
    if (!response.ok) throw new Error(`服务器返回错误（HTTP ${response.status}）`)
    cats.value = cats.value.filter((item) => item.id !== cat.id)
    storageError.value = ''
    navigate('/cats')
  } catch (error) {
    storageError.value = error instanceof Error
      ? `删除失败：${error.message}。请稍后重试。`
      : '删除失败。请稍后重试。'
  }
}

function formatDate(value: string) {
  if (!value) return '还没有填写'
  const date = new Date(`${value}T00:00:00`)
  if (Number.isNaN(date.getTime())) return value
  return new Intl.DateTimeFormat('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' }).format(date)
}

type MessageResponse = { message: string }
const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'
const message = ref('')
const errorMessage = ref('')
const isLoading = ref(false)
const statusLabel = computed(() => {
  if (isLoading.value) return '正在连接后端'
  if (errorMessage.value) return '后端暂不可用'
  return message.value || '等待连接'
})

async function fetchMessage() {
  isLoading.value = true
  errorMessage.value = ''
  try {
    const response = await fetch(`${apiBaseUrl}/api/message`)
    if (!response.ok) throw new Error(`服务器返回错误（HTTP ${response.status}）`)
    const data = await response.json() as MessageResponse
    if (!data.message) throw new Error('接口响应中没有 message 字段')
    message.value = data.message
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : '请求失败'
  } finally {
    isLoading.value = false
  }
}

const features = [
  { icon: 'profile', title: '基本资料', text: '名字、品种、生日、性格，每只猫一张清楚的档案卡。' },
  { icon: 'weight', title: '体重记录', text: '定期记一笔，体重变化一目了然，胖瘦心里有数。' },
  { icon: 'vaccine', title: '疫苗驱虫', text: '记录接种和驱虫日期，到期前提醒，不再靠记性。' },
  { icon: 'clinic', title: '就诊记录', text: '症状、诊断、用药和复诊时间，看病时随手就能翻。' },
] as const
const steps = [
  { title: '添加猫咪', text: '为家里的每只猫建立档案，填写基本信息。' },
  { title: '随手记录', text: '称体重、打疫苗、去医院，家里任何人都能记。' },
  { title: '按时提醒', text: '疫苗、驱虫、复诊快到期时，在首页提前看到。' },
]

onMounted(() => {
  void loadCats()
  syncRoute()
  window.addEventListener('hashchange', syncRoute)
  void fetchMessage()
})
onBeforeUnmount(() => window.removeEventListener('hashchange', syncRoute))
</script>

<template>
  <template v-if="view === 'home'">
    <a class="skip-link" href="#main">跳到主要内容</a>
    <header class="topbar">
      <div class="container topbar-inner">
        <a class="brand" href="#top"><BrandMark />喵家档案</a>
        <nav class="nav" aria-label="页面导航">
          <a href="#features">功能</a><a href="#steps">使用方法</a><a href="#start">开始</a>
        </nav>
        <button class="btn btn-primary btn-sm" type="button" @click="navigate('/cats')">我的猫咪</button>
      </div>
    </header>

    <main id="main">
      <section id="top" class="container hero" aria-labelledby="hero-title">
        <div class="hero-copy">
          <p class="eyebrow">多猫家庭记录系统</p>
          <h1 id="hero-title">每一只猫，<br />都有自己的档案</h1>
          <p class="lead">体重、饮食、疫苗、驱虫和就诊，一家人一起记录，一起照顾。不用再翻聊天记录找上次打针的日期。</p>
          <div class="actions">
            <button class="btn btn-primary" type="button" @click="navigate('/cats')">开始记录</button>
            <a class="btn btn-secondary" href="#features">了解功能</a>
          </div>
        </div>
        <div class="hero-art">
          <div class="photo-album" aria-label="一只在窗边休息的猫咪照片">
            <div class="photo-tape" aria-hidden="true"></div>
            <img src="/welcome-cat.jpg" alt="一只在窗边休息的灰色虎斑猫" />
          </div>
        </div>
      </section>

      <section id="features" class="section" aria-labelledby="features-title">
        <div class="container">
          <div class="section-head">
            <p class="eyebrow">功能</p><h2 id="features-title">照顾猫咪需要记住的事，都放在这里</h2>
            <p>四类记录覆盖日常照护，家人之间共享同一份信息。</p>
          </div>
          <div class="feature-grid">
            <article v-for="feature in features" :key="feature.title" class="feature">
              <div class="feature-icon"><FeatureIcon :name="feature.icon" /></div>
              <h3>{{ feature.title }}</h3><p>{{ feature.text }}</p>
            </article>
          </div>
        </div>
      </section>

      <section id="steps" class="section" aria-labelledby="steps-title">
        <div class="container">
          <div class="section-head"><p class="eyebrow">使用方法</p><h2 id="steps-title">三步开始</h2></div>
          <ol class="steps">
            <li v-for="(step, index) in steps" :key="step.title" class="step">
              <span class="step-num" aria-hidden="true">{{ index + 1 }}</span><h3>{{ step.title }}</h3><p>{{ step.text }}</p>
            </li>
          </ol>
        </div>
      </section>

      <section id="start" class="section" aria-labelledby="cta-title">
        <div class="container">
          <div class="cta">
            <h2 id="cta-title">为你家的猫建立第一份档案</h2>
            <p>从名字和一张照片开始，之后的每一次称重和体检都会被好好记下。</p>
            <div class="actions"><button class="btn btn-primary" type="button" @click="startNewCat">创建猫咪档案</button></div>
          </div>
        </div>
      </section>
    </main>

    <footer class="footer"><div class="container footer-inner">
      <span>喵家档案 · 为家里的每一只猫</span>
      <span class="status" :class="{ 'is-online': message, 'is-error': errorMessage, 'is-loading': isLoading }" aria-live="polite">
        <span class="status-dot" aria-hidden="true"></span><span>{{ statusLabel }}</span>
        <button v-if="errorMessage" class="status-retry" type="button" @click="fetchMessage">重试</button>
      </span>
    </div></footer>
  </template>

  <template v-else>
    <a class="skip-link" href="#archive-main">跳到档案内容</a>
    <header class="topbar">
      <div class="container topbar-inner archive-topbar">
        <button class="brand brand-button" type="button" @click="navigate('/')"><BrandMark />喵家档案</button>
        <span class="archive-topbar-note">每一份陪伴，都值得被记下来</span>
        <button class="btn btn-primary btn-sm" type="button" @click="startNewCat">＋ 添加猫咪</button>
      </div>
    </header>

    <main id="archive-main" class="container archive-main">
      <div v-if="storageError" class="notice notice-error" role="alert">
        <span>{{ storageError }}</span><button type="button" aria-label="关闭提示" @click="storageError = ''">×</button>
      </div>
      <div v-if="notice" class="notice notice-success" role="status">
        <span>{{ notice }}</span><button type="button" aria-label="关闭提示" @click="notice = ''">×</button>
      </div>

      <template v-if="view === 'list'">
        <div class="archive-heading">
          <div><p class="eyebrow">我的家庭成员</p><h1>猫咪档案</h1><p class="archive-subtitle">{{ cats.length ? `家里有 ${cats.length} 只猫咪` : '把家里每一位小成员都好好记录下来。' }}</p></div>
          <button class="btn btn-primary" type="button" @click="startNewCat">＋ 创建猫咪档案</button>
        </div>

        <div v-if="cats.length" class="archive-toolbar">
          <label class="search-box"><span aria-hidden="true">⌕</span><input v-model="search" type="search" placeholder="搜索名字或品种" aria-label="搜索猫咪名字或品种" /></label>
          <span class="record-count">{{ visibleCats.length }} 份档案</span>
        </div>

        <div v-if="cats.length && visibleCats.length" class="cat-grid">
          <button v-for="cat in visibleCats" :key="cat.id" class="cat-card" type="button" @click="openCat(cat)">
            <div class="cat-card-photo">
              <img v-if="cat.photo" :src="cat.photo" :alt="`${cat.name}的照片`" />
              <span v-else class="cat-placeholder" aria-hidden="true"><BrandMark /></span>
              <span class="photo-label">家庭档案</span>
            </div>
            <span class="cat-card-body"><strong>{{ cat.name }}</strong><span>{{ cat.breed || '品种未填写' }}</span><span class="cat-card-meta">{{ cat.gender || '性别未填写' }}<template v-if="cat.birthday"> · {{ formatDate(cat.birthday) }}出生</template></span></span>
            <span class="cat-card-arrow" aria-hidden="true">↗</span>
          </button>
          <button class="cat-add-card" type="button" @click="startNewCat"><span>＋</span><strong>添加另一只猫</strong><small>继续为家人建立档案</small></button>
        </div>

        <section v-else-if="cats.length" class="empty-state compact-empty">
          <span class="empty-icon" aria-hidden="true">⌕</span><h2>没有找到这只猫</h2><p>试试其他名字或品种。</p>
        </section>

        <section v-else class="empty-state">
          <div class="empty-illustration" aria-hidden="true"><BrandMark /></div>
          <p class="eyebrow">第一份家庭档案</p><h2>还没有猫咪档案</h2>
          <p>从名字开始，慢慢补上照片、生日和它的小习惯。</p>
          <button class="btn btn-primary" type="button" @click="startNewCat">创建第一份档案</button>
        </section>
        <button class="back-home-link" type="button" @click="navigate('/')">← 返回首页</button>
      </template>

      <template v-else-if="view === 'form'">
        <button class="back-home-link form-back" type="button" @click="navigate(editingId ? `/cats/${encodeURIComponent(editingId)}` : '/cats')">← {{ editingId ? '返回档案' : '返回猫咪列表' }}</button>
        <div class="archive-heading form-heading"><div><p class="eyebrow">{{ editingId ? '更新家庭成员资料' : '新的家庭成员' }}</p><h1>{{ editingId ? '编辑猫咪档案' : '创建猫咪档案' }}</h1><p class="archive-subtitle">带 <span class="required-mark">*</span> 的项目需要填写，其他信息之后也可以补充。</p></div></div>
        <form class="cat-form" novalidate @submit.prevent="saveCat">
          <section class="form-section">
            <div class="form-section-heading"><span>01</span><div><h2>基本资料</h2><p>先告诉我们它是谁。</p></div></div>
            <div class="form-grid">
              <label class="field field-required" for="cat-name"><span>猫咪名字 <b>*</b></span><input id="cat-name" v-model="form.name" type="text" maxlength="40" autocomplete="off" placeholder="例如：小橘" :aria-invalid="Boolean(nameError)" aria-describedby="name-error" /><small v-if="nameError" id="name-error" class="field-error">{{ nameError }}</small></label>
              <label class="field" for="cat-breed"><span>品种</span><input id="cat-breed" v-model="form.breed" type="text" maxlength="60" placeholder="例如：中华田园猫" /></label>
              <label class="field" for="cat-birthday"><span>生日</span><input id="cat-birthday" v-model="form.birthday" type="date" :max="new Date().toISOString().slice(0, 10)" /></label>
              <label class="field" for="cat-gender"><span>性别</span><select id="cat-gender" v-model="form.gender"><option value="">暂不填写</option><option value="公猫">公猫</option><option value="母猫">母猫</option><option value="未知">不确定</option></select></label>
              <label class="field field-wide" for="cat-personality"><span>性格关键词</span><input id="cat-personality" v-model="form.personality" type="text" maxlength="100" placeholder="例如：亲人、爱晒太阳、胆子小" /><small>用逗号分开几个词就可以。</small></label>
            </div>
          </section>

          <section class="form-section">
            <div class="form-section-heading"><span>02</span><div><h2>照片和备注</h2><p>留下它最可爱的样子，也记下需要注意的事。</p></div></div>
            <div class="form-grid">
              <div class="field field-wide"><span>猫咪照片</span>
                <div class="photo-picker">
                  <div class="photo-preview"><img v-if="form.photo" :src="form.photo" :alt="`${form.name || '猫咪'}照片预览`" /><BrandMark v-else class="photo-placeholder-icon" /></div>
                  <div class="photo-picker-copy"><label class="btn btn-secondary photo-upload" for="cat-photo">{{ isReadingPhoto ? '正在处理照片…' : form.photo ? '更换照片' : '选择一张照片' }}</label><input id="cat-photo" class="visually-hidden" type="file" accept="image/jpeg,image/png,image/webp,image/gif" :disabled="isReadingPhoto" @change="readPhoto" /><small>支持 JPG、PNG、WebP 或 GIF，最大 8 MB。</small><button v-if="form.photo" class="text-button" type="button" @click="removePhoto">移除照片</button><small v-if="photoError" class="field-error">{{ photoError }}</small></div>
                </div>
              </div>
              <label class="field field-wide" for="cat-notes"><span>想记下的话</span><textarea id="cat-notes" v-model="form.notes" rows="4" maxlength="1000" placeholder="喜欢吃什么、有什么小习惯，或者需要留心的事情…"></textarea><small>{{ form.notes.length }}/1000</small></label>
            </div>
          </section>

          <div v-if="storageError" class="notice notice-error form-notice" role="alert"><span>{{ storageError }}</span><button type="button" aria-label="关闭提示" @click="storageError = ''">×</button></div>
          <div class="form-actions"><button class="btn btn-secondary" type="button" :disabled="isSaving" @click="navigate(editingId ? `/cats/${encodeURIComponent(editingId)}` : '/cats')">取消</button><button class="btn btn-primary" type="submit" :disabled="isSaving || isReadingPhoto">{{ isSaving ? '正在保存…' : editingId ? '保存修改' : '保存档案' }}</button></div>
        </form>
      </template>

      <template v-else-if="view === 'detail'">
        <button class="back-home-link form-back" type="button" @click="navigate('/cats')">← 返回猫咪列表</button>
        <section v-if="selectedCat" class="cat-detail">
          <div class="detail-photo"><img v-if="selectedCat.photo" :src="selectedCat.photo" :alt="`${selectedCat.name}的照片`" /><BrandMark v-else class="detail-placeholder-icon" /><div class="detail-photo-tape" aria-hidden="true"></div></div>
          <div class="detail-content"><p class="eyebrow">喵家档案 · 家庭成员</p><h1>{{ selectedCat.name }}</h1><p class="detail-breed">{{ selectedCat.breed || '品种未填写' }}</p>
            <dl class="detail-fields"><div><dt>生日</dt><dd>{{ formatDate(selectedCat.birthday) }}</dd></div><div><dt>性别</dt><dd>{{ selectedCat.gender || '还没有填写' }}</dd></div><div class="detail-field-wide"><dt>性格关键词</dt><dd>{{ selectedCat.personality || '还没有填写' }}</dd></div><div class="detail-field-wide"><dt>想记下的话</dt><dd class="detail-notes">{{ selectedCat.notes || '还没有留下备注。之后可以在编辑档案时补充。' }}</dd></div></dl>
            <p class="detail-updated">最近保存于 {{ formatDate(selectedCat.updatedAt.slice(0, 10)) }}</p>
            <div class="detail-actions"><button class="btn btn-primary" type="button" @click="editCat(selectedCat)">编辑档案</button><button class="btn btn-secondary" type="button" @click="navigate('/cats')">查看其他猫咪</button><button class="text-button delete-button" type="button" @click="deleteCat(selectedCat)">删除档案</button></div>
          </div>
        </section>
        <section v-else class="empty-state detail-missing"><span class="empty-icon" aria-hidden="true">?</span><h2>找不到这份档案</h2><p>它可能已经被删除，返回列表继续查看其他猫咪。</p><button class="btn btn-primary" type="button" @click="navigate('/cats')">返回猫咪列表</button></section>
      </template>
    </main>

    <footer class="footer archive-footer"><div class="container footer-inner">
      <button class="back-home-link" type="button" @click="navigate('/')">喵家档案 · 返回首页</button>
      <span class="status" :class="{ 'is-online': message, 'is-error': errorMessage, 'is-loading': isLoading }" aria-live="polite"><span class="status-dot" aria-hidden="true"></span><span>{{ statusLabel }}</span><button v-if="errorMessage" class="status-retry" type="button" @click="fetchMessage">重试</button></span>
    </div></footer>
  </template>
</template>
