<script setup>
import DefaultTheme from 'vitepress/theme'
import { useRoute } from 'vitepress'
import { nextTick, onMounted, onUnmounted, watch } from 'vue'

const { Layout } = DefaultTheme
const route = useRoute()

let observer = null

function updateHashOnScroll() {
  if (typeof window === 'undefined' || typeof document === 'undefined') {
    return
  }

  if (observer) {
    observer.disconnect()
    observer = null
  }

  const headings = document.querySelectorAll(
    '.vp-doc h2[id], .vp-doc h3[id], .vp-doc h4[id]'
  )

  if (!headings.length) {
    return
  }

  const observerOptions = {
    root: null,
    rootMargin: '-80px 0px -70% 0px',
    threshold: 0
  }

  observer = new IntersectionObserver((entries) => {
    // Find intersecting headings
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        const id = entry.target.getAttribute('id')
        if (id) {
          const newHash = `#${id}`
          if (window.location.hash !== newHash) {
            const currentPath = window.location.pathname + window.location.search
            window.history.replaceState(history.state, '', currentPath + newHash)
          }
        }
      }
    })
  }, observerOptions)

  headings.forEach((h) => observer.observe(h))
}

onMounted(() => {
  nextTick(() => {
    updateHashOnScroll()
  })
})

watch(
  () => route.path,
  () => {
    nextTick(() => {
      updateHashOnScroll()
    })
  }
)

onUnmounted(() => {
  if (observer) {
    observer.disconnect()
    observer = null
  }
})
</script>

<template>
  <Layout />
</template>
