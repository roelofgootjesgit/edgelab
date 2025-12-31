/* Strategy Template Selector Styles */

.template-selector {
  padding: 2rem 0;
}

.template-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
  max-width: 1200px;
  margin: 0 auto;
}

.template-card {
  background: white;
  border-radius: 16px;
  padding: 2rem;
  text-align: center;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  border: 2px solid #e2e8f0;
  position: relative;
  overflow: hidden;
}

.template-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, 
    var(--accent-blue) 0%, 
    var(--accent-purple) 100%
  );
  transform: scaleX(0);
  transition: transform 0.3s ease;
}

.template-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.15);
  border-color: var(--accent-blue);
}

.template-card:hover::before {
  transform: scaleX(1);
}

.template-card:active {
  transform: translateY(-4px);
}

.template-icon {
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

.template-name {
  font-weight: 700;
}

.template-description {
  line-height: 1.5;
  min-height: 3rem;
}

.template-conditions {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #e2e8f0;
}

/* Responsive */
@media (max-width: 768px) {
  .template-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .template-card {
    padding: 1.5rem;
  }
}

/* Hover effects for different colors */
.template-card[data-template-id="scratch"]:hover {
  border-color: var(--accent-blue);
  box-shadow: 0 12px 32px rgba(59, 130, 246, 0.2);
}

.template-card[data-template-id="ict_smc"]:hover {
  border-color: var(--accent-purple);
  box-shadow: 0 12px 32px rgba(139, 92, 246, 0.2);
}

.template-card[data-template-id="trend_following"]:hover {
  border-color: #10b981;
  box-shadow: 0 12px 32px rgba(16, 185, 129, 0.2);
}

.template-card[data-template-id="mean_reversion"]:hover {
  border-color: #ec4899;
  box-shadow: 0 12px 32px rgba(236, 72, 153, 0.2);
}

.template-card[data-template-id="breakout_momentum"]:hover {
  border-color: #f59e0b;
  box-shadow: 0 12px 32px rgba(245, 158, 11, 0.2);
}

.template-card[data-template-id="custom_templates"]:hover {
  border-color: var(--accent-cyan);
  box-shadow: 0 12px 32px rgba(34, 211, 238, 0.2);
}