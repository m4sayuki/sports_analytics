const STORAGE_KEY = "motion-pilot-view-state";

const viewModes = {
  overlay: {
    label: "Overlay Mode",
    clip: "100m Start / Clip A",
    athlete: "Aoi Sato",
    playbar: 38,
    tilt: "42°",
    tiltDelta: "理想との差 -4°",
    ground: "0.14s",
    groundDelta: "前回より -0.02s",
    insightTitle: "1歩目で上体が少し早く起きる",
    insightBody: "ブロック解除後の2フレームだけ頭の高さを維持すると、推進方向が安定しやすくなります。",
  },
  compare: {
    label: "Compare Replay",
    clip: "100m Start / Best vs Current",
    athlete: "Aoi Sato",
    playbar: 61,
    tilt: "46°",
    tiltDelta: "ベストとの差 +1°",
    ground: "0.11s",
    groundDelta: "ベスト比 -0.01s",
    insightTitle: "腕振りの同期が改善している",
    insightBody: "接地直前の腕の切り返しが揃い、1歩目の推進がより前方へ向いています。",
  },
  heatmap: {
    label: "Heat Motion",
    clip: "Return Test / Front View",
    athlete: "Aoi Sato",
    playbar: 52,
    tilt: "39°",
    tiltDelta: "理想との差 -7°",
    ground: "0.16s",
    groundDelta: "前回より +0.01s",
    insightTitle: "左脚の引き込みが少し浅い",
    insightBody: "接地前の準備が遅れやすいので、遊脚の回収を小さなドリルで揃えると見やすくなります。",
  },
};

const defaultState = { view: "overlay" };
const state = loadState();
const viewTabs = document.querySelector("#viewTabs");

function loadState() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (!saved) {
      return { ...defaultState };
    }

    return { ...defaultState, ...JSON.parse(saved) };
  } catch (error) {
    return { ...defaultState };
  }
}

function saveState() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
}

function renderTabs() {
  [...viewTabs.querySelectorAll(".tab")].forEach((tab) => {
    tab.classList.toggle("is-active", tab.dataset.view === state.view);
  });
}

function render() {
  const current = viewModes[state.view];
  document.querySelector("#viewModeLabel").textContent = current.label;
  document.querySelector("#clipLabel").textContent = current.clip;
  document.querySelector("#athleteLabel").textContent = current.athlete;
  document.querySelector("#playbarFill").style.width = `${current.playbar}%`;
  document.querySelector("#metricTilt").textContent = current.tilt;
  document.querySelector("#metricTiltDelta").textContent = current.tiltDelta;
  document.querySelector("#metricGround").textContent = current.ground;
  document.querySelector("#metricGroundDelta").textContent = current.groundDelta;
  document.querySelector("#insightTitle").textContent = current.insightTitle;
  document.querySelector("#insightBody").textContent = current.insightBody;
  document.querySelector("#stagePanel").className = `stage mode-${state.view}`;
  renderTabs();
  saveState();
}

viewTabs.addEventListener("click", (event) => {
  const button = event.target.closest("[data-view]");
  if (!button) {
    return;
  }

  state.view = button.dataset.view;
  render();
});

render();
