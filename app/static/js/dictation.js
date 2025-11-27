(() => {
  let player;
  let currentSegmentIndex = 0;
  let currentSegment = (window.SEGMENTS || [])[0];
  let errorCount = 0;
  let isPlaying = false;

  const dictationInput = document.getElementById('dictationInput');
  const progressFill = document.getElementById('progressFill');
  const progressStat = document.getElementById('progressStat');
  const errorCountEl = document.getElementById('errorCount');
  const sentenceNumberEl = document.getElementById('sentenceNumber');
  const successMessage = document.getElementById('successMessage');
  const listeningHint = document.getElementById('listeningHint');
  const replayButton = document.getElementById('replayButton');
  const backButton = document.getElementById('backButton');

  // Public callback for YouTube IFrame API
  window.onYouTubeIframeAPIReady = function () {
    player = new YT.Player('player', {
      height: '400',
      width: '100%',
      videoId: window.VIDEO_ID,
      playerVars: { controls: 1, modestbranding: 1, rel: 0 },
      events: { onReady: onPlayerReady, onStateChange: onPlayerStateChange }
    });
  };

  function onPlayerReady() {
    updateBackButtonState();
    if (Array.isArray(window.SEGMENTS) && window.SEGMENTS.length) {
      currentSegmentIndex = 0;
      currentSegment = window.SEGMENTS[currentSegmentIndex];
      playCurrentSegment();
    }
  }

  function onPlayerStateChange(event) {
    if (event.data === YT.PlayerState.PLAYING) {
      isPlaying = true;
      checkSegmentEnd();
    } else if (event.data === YT.PlayerState.PAUSED) {
      isPlaying = false;
    }
  }

  function playCurrentSegment() {
    if (!player || !player.seekTo) return;
    currentSegment = window.SEGMENTS[currentSegmentIndex];
    player.seekTo(currentSegment.start, true);
    player.playVideo();

    // Reset UI for listening phase
    setHint('Listen carefully to the video segment…', '#fff3cd', '#ffc107', '#856404');
    dictationInput.value = '';
    dictationInput.disabled = true;
    dictationInput.classList.remove('correct', 'error');
    setProgress(0);
  }

  function checkSegmentEnd() {
    if (!isPlaying) return;
    const currentTime = player.getCurrentTime();
    if (currentTime >= currentSegment.end) {
      player.pauseVideo();
      enableTyping();
    } else {
      setTimeout(checkSegmentEnd, 100);
    }
  }

  function enableTyping() {
    setHint('Now type what you heard!', '#d1ecf1', '#17a2b8', '#0c5460');
    dictationInput.disabled = false;
    dictationInput.focus();
  }

  function updateBackButtonState() {
    backButton.disabled = currentSegmentIndex === 0;
  }

  function goToPreviousSegment() {
    if (currentSegmentIndex > 0) {
      currentSegmentIndex--;
      sentenceNumberEl.textContent = currentSegmentIndex + 1;
      successMessage.classList.remove('show');
      playCurrentSegment();
      updateBackButtonState();
    }
  }

  function setProgress(pct) {
    const clamped = Math.max(0, Math.min(100, pct));
    progressFill.style.width = clamped + '%';
    progressStat.textContent = Math.round(clamped) + '%';
  }

  function setHint(text, bg, border, color) {
    listeningHint.textContent = text;
    listeningHint.style.background = bg;
    listeningHint.style.borderColor = border;
    listeningHint.style.color = color;
  }

  // Bind buttons
  replayButton?.addEventListener('click', playCurrentSegment);
  backButton?.addEventListener('click', goToPreviousSegment);

  // Input validation
  dictationInput?.addEventListener('input', function (e) {
    const typed = e.target.value;
    const expected = currentSegment.text.substring(0, typed.length);
    if (typed === expected) {
      dictationInput.classList.remove('error');
      dictationInput.classList.add('correct');
      const pct = (typed.length / currentSegment.text.length) * 100;
      setProgress(pct);
      if (typed === currentSegment.text) {
        handleSegmentComplete();
      }
    } else {
      // revert last char
      e.target.value = typed.substring(0, typed.length - 1);
      dictationInput.classList.add('error');
      errorCount += 1;
      errorCountEl.textContent = String(errorCount);
      setTimeout(() => dictationInput.classList.remove('error'), 300);
    }
  });

  function handleSegmentComplete() {
    successMessage.classList.add('show');
    successMessage.textContent = 'Perfect! Moving to next segment…';
    dictationInput.disabled = true;
    setTimeout(() => {
      currentSegmentIndex++;
      successMessage.classList.remove('show');
      if (currentSegmentIndex < window.SEGMENTS.length) {
        sentenceNumberEl.textContent = currentSegmentIndex + 1;
        updateBackButtonState();
        playCurrentSegment();
      } else {
        completeExercise();
      }
    }, 1500);
  }

  function completeExercise() {
    setHint('Congratulations! You completed all segments!', '#d4edda', '#28a745', '#155724');
    successMessage.textContent = 'Exercise completed! Total errors: ' + errorCount;
    successMessage.classList.add('show');
    replayButton.textContent = 'Restart Exercise';
    replayButton.onclick = () => window.location.reload();
  }
})();

