import numpy as np
import mdp
import cv2


def ICA(self, pc_list, ch=-1):
    fast_ICA_node = mdp.nodes.FastICANode()
    self._IC_signals = fast_ICA_node(self.oPC_signals(ch=ch)[:, pc_list])
    self._ICs = np.tensordot(np.tensordot(self.oPCs(ch=ch)[:, :, pc_list],
                                          fast_ICA_node.white.v, 1),
                             fast_ICA_node.filters, 1)


def ICs(self, pc_list, smooth_size=0, ch=-1):
    if not hasattr(self, '_ICs'):
        self.ICA(pc_list, ch=ch)
    if smooth_size:
        ret = np.zeros(self._ICs.shape)
        for i in range(ret.shape[2]):
            m = np.min(self._ICs[:, :, i])
            ret[:, :, i] = m + cv2.GaussianBlur(
                self._ICs[:, :, i] - m, (smooth_size, smooth_size), 0
            )
        return ret
    else:
        return self._ICs
