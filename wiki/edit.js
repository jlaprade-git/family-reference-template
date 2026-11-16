/**
 * Inline WYSIWYG editor for the family wiki.
 * Adds an Edit/Save button to every page.
 * Uses a bundled copy of open-source TinyMCE (wiki/vendor/tinymce), so it works fully offline.
 */
(function () {
  // Don't run on the landing page (no <main> with class "main")
  var mainEl = document.querySelector("main.main");
  if (!mainEl) return;

  // Current page path relative to wiki root
  var pagePath = window.location.pathname.replace(/^\//, "") || "index.html";

  // ── Create the edit toolbar ──
  var toolbar = document.createElement("div");
  toolbar.id = "wiki-toolbar";
  toolbar.style.cssText =
    "position:fixed;bottom:1.5rem;right:1.5rem;z-index:9999;" +
    "display:flex;gap:0.5rem;align-items:center;";

  var editBtn = document.createElement("button");
  editBtn.textContent = "Edit Page";
  editBtn.style.cssText =
    "padding:0.6rem 1.2rem;border:none;border-radius:6px;cursor:pointer;" +
    "font-size:0.9rem;font-weight:600;background:#4ecca3;color:#1a1a2e;" +
    "box-shadow:0 2px 8px rgba(0,0,0,0.3);";

  var saveBtn = document.createElement("button");
  saveBtn.textContent = "Save";
  saveBtn.style.cssText =
    "padding:0.6rem 1.2rem;border:none;border-radius:6px;cursor:pointer;" +
    "font-size:0.9rem;font-weight:600;background:#e94560;color:#fff;" +
    "box-shadow:0 2px 8px rgba(0,0,0,0.3);display:none;";

  var cancelBtn = document.createElement("button");
  cancelBtn.textContent = "Cancel";
  cancelBtn.style.cssText =
    "padding:0.6rem 1.2rem;border:none;border-radius:6px;cursor:pointer;" +
    "font-size:0.9rem;font-weight:600;background:#2a2a4a;color:#eaeaea;" +
    "box-shadow:0 2px 8px rgba(0,0,0,0.3);display:none;";

  var status = document.createElement("span");
  status.style.cssText =
    "color:#4ecca3;font-size:0.85rem;font-weight:600;display:none;";

  var printBtn = document.createElement("button");
  printBtn.textContent = "Print All";
  printBtn.style.cssText =
    "padding:0.6rem 1.2rem;border:none;border-radius:6px;cursor:pointer;" +
    "font-size:0.9rem;font-weight:600;background:#f5c542;color:#1a1a2e;" +
    "box-shadow:0 2px 8px rgba(0,0,0,0.3);";
  printBtn.addEventListener("click", function () {
    // Detect which person section we are in
    var section = window.location.pathname.indexOf("/person2/") !== -1 ? "person2" : "person1";
    window.open("/print-all?section=" + section, "_blank");
  });

  toolbar.appendChild(printBtn);
  toolbar.appendChild(editBtn);
  toolbar.appendChild(saveBtn);
  toolbar.appendChild(cancelBtn);
  toolbar.appendChild(status);
  document.body.appendChild(toolbar);

  var originalContent = "";
  var editorLoaded = false;
  var editorActive = false;

  // ── Load the bundled TinyMCE (no internet needed) ──
  function loadTinyMCE(callback) {
    if (editorLoaded) {
      callback();
      return;
    }
    var script = document.createElement("script");
    script.src = "/vendor/tinymce/tinymce.min.js";
    script.onload = function () {
      editorLoaded = true;
      callback();
    };
    script.onerror = function () {
      alert("Failed to load editor. Missing wiki/vendor/tinymce.");
    };
    document.head.appendChild(script);
  }

  // ── Enter edit mode ──
  editBtn.addEventListener("click", function () {
    editBtn.textContent = "Loading...";
    editBtn.disabled = true;

    loadTinyMCE(function () {
      originalContent = mainEl.innerHTML;

      // Give main an ID for TinyMCE to target
      mainEl.id = "wiki-editable";

      tinymce.init({
        selector: "#wiki-editable",
        inline: true,
        menubar: true,
        plugins:
          "advlist autolink lists link charmap preview anchor searchreplace " +
          "visualblocks code fullscreen insertdatetime table help wordcount",
        toolbar:
          "undo redo | blocks | bold italic underline strikethrough | " +
          "alignleft aligncenter alignright | bullist numlist outdent indent | " +
          "link table | code | removeformat",
        content_css: false,
        skin: "oxide-dark",
        content_style:
          "body { font-family: 'Segoe UI', system-ui, sans-serif; color: #eaeaea; }",
        promotion: false,
        branding: false,
        license_key: "gpl",
        setup: function (editor) {
          editor.on("init", function () {
            editorActive = true;
            editBtn.style.display = "none";
            editBtn.textContent = "Edit Page";
            editBtn.disabled = false;
            saveBtn.style.display = "inline-block";
            cancelBtn.style.display = "inline-block";
          });
        },
      });
    });
  });

  // ── Save ──
  saveBtn.addEventListener("click", function () {
    if (!editorActive) return;

    var editor = tinymce.activeEditor;
    if (editor) {
      editor.save();
    }
    var content = mainEl.innerHTML;

    // Clean up TinyMCE artifacts from the saved HTML
    var temp = document.createElement("div");
    temp.innerHTML = content;
    // Remove TinyMCE-added attributes and elements
    var mceEls = temp.querySelectorAll("[data-mce-bogus], .mce-content-body");
    mceEls.forEach(function (el) {
      el.removeAttribute("data-mce-bogus");
      el.removeAttribute("data-mce-style");
      el.removeAttribute("data-mce-href");
      el.classList.remove("mce-content-body");
    });
    temp.querySelectorAll("[id='wiki-editable']").forEach(function (el) {
      el.removeAttribute("id");
    });
    content = temp.innerHTML;

    // Destroy editor
    if (editor) {
      editor.destroy();
    }
    editorActive = false;

    saveBtn.style.display = "none";
    cancelBtn.style.display = "none";
    status.textContent = "Saving...";
    status.style.display = "inline";

    fetch("/save", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ path: pagePath, content: content }),
    })
      .then(function (resp) {
        return resp.json();
      })
      .then(function (data) {
        if (data.ok) {
          status.textContent = "Saved!";
          status.style.color = "#4ecca3";
          setTimeout(function () {
            status.style.display = "none";
            editBtn.style.display = "inline-block";
          }, 2000);
        } else {
          status.textContent = "Error: " + (data.error || "Unknown");
          status.style.color = "#e94560";
          editBtn.style.display = "inline-block";
        }
      })
      .catch(function (err) {
        status.textContent = "Error: " + err.message;
        status.style.color = "#e94560";
        editBtn.style.display = "inline-block";
      });
  });

  // ── Cancel ──
  cancelBtn.addEventListener("click", function () {
    var editor = tinymce.activeEditor;
    if (editor) {
      editor.destroy();
    }
    mainEl.innerHTML = originalContent;
    editorActive = false;
    saveBtn.style.display = "none";
    cancelBtn.style.display = "none";
    editBtn.style.display = "inline-block";
  });
})();
